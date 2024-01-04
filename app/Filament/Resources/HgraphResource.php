<?php

namespace App\Filament\Resources;

use Filament\Forms;
use Filament\Tables;
use App\Models\Hgraph;
use Filament\Infolists;
use Filament\Forms\Form;
use Filament\Tables\Table;
use Filament\Infolists\Infolist;
use Filament\Resources\Resource;
use Filament\Infolists\Components;
use Filament\Tables\Filters\Filter;
use Filament\Forms\Components\Textarea;
use Filament\Infolists\Components\Tabs;
use Filament\Tables\Actions\EditAction;
use Filament\Tables\Actions\ViewAction;
use Filament\Forms\Components\TextInput;
use Filament\Tables\Filters\SelectFilter;
use Filament\Infolists\Components\ViewEntry;
use App\Filament\Resources\HgraphResource\Pages;
use Illuminate\Contracts\Database\Eloquent\Builder;
use Illuminate\Support\HtmlString;

class HgraphResource extends Resource
{
    protected static ?string $model = Hgraph::class;

    protected static ?string $navigationIcon = 'heroicon-o-rectangle-stack';

    protected static ?string $recordTitleAttribute = 'name';

    public static ?string $navigationLabel = 'Hypergraphs';

    public static ?string $pluralLabel = 'Hypergraphs';


    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\TextInput::make('name')
                    ->required()
                    ->maxLength(255),
                // Forms\Components\TextInput::make('category')
                // ->multiple()
                //     ->maxLength(255),
                Forms\Components\Textarea::make('description')
                ->label('README.md')
                ->rows(20)
                    ->columnSpanFull(),
                Forms\Components\TextInput::make('nodes')
                    ->numeric(),
                Forms\Components\TextInput::make('edges')
                    ->numeric(),
                Forms\Components\TextInput::make('dnodemax')
                    ->numeric(),
                Forms\Components\TextInput::make('dedgemax')
                    ->numeric(),
                Forms\Components\TextInput::make('dnodeavg')
                    ->numeric(),
                Forms\Components\TextInput::make('dedgeavg')
                    ->numeric(),
                Forms\Components\Textarea::make('dnodes')
                    ->columnSpanFull(),
                Forms\Components\Textarea::make('dedges')
                    ->columnSpanFull(),
            ]);
    }
    public static function infolist(Infolist $infolist): Infolist
    {
        return $infolist
            ->schema([
                Tabs::make('Tabs')
                ->columnSpan('full')
                ->persistTabInQueryString()
                ->tabs([
                    Tabs\Tab::make('Graph data')
                    ->schema([
                        Components\Section::make()
                        ->key('section1')
                        ->headerActions([
                            \Filament\Infolists\Components\Actions\Action::make('download')
                                ->color('success')
                                ->label(
                                    fn ($record):string => 'Download ('.round(filesize(storage_path('/app/public/datasets/'.$record->name.'/'.$record->name.'.hgf'))/1000000, 2).' MB)'
                                )
                                ->icon('heroicon-o-arrow-down-tray')
                                ->action(function ($record,  \Filament\Infolists\Components\Actions\Action $action) {
                                    redirect()->to($record->url);
                                })
                                // ->action(function () {
                                //     // ...
                                // }),
                        ])
                        ->schema([
                            Components\Grid::make(4)
                            ->schema([
                                Components\Group::make([
                                    Infolists\Components\TextEntry::make('name')->badge(),
                                    Infolists\Components\TextEntry::make('categories.type')->label('Categories')->badge(),
                                    Infolists\Components\TextEntry::make('author')->badge()->color('success'),
                                    Infolists\Components\TextEntry::make('authorurl')->badge()->color('success')->url(
                                        fn ($record):string => $record->authorurl
                                    )->openUrlInNewTab(),
                                    Infolists\Components\TextEntry::make('created_at')->badge(),
                                    Infolists\Components\TextEntry::make('updated_at')->badge()
                                ]),
                                Components\Group::make([
                                    Infolists\Components\TextEntry::make('nodes')
                                    ->label('|V|')
                                    ->badge(),
                                    Infolists\Components\TextEntry::make('edges')
                                    ->label('|E|')
                                    ->badge(),
                                    Infolists\Components\TextEntry::make('dnodemax')
                                    ->label(fn() => new HtmlString('d<sub>max</sub>'))
                                    ->badge(),
                                    Infolists\Components\TextEntry::make('dnodeavg')
                                    ->label(fn() => new HtmlString('d<sub>avg</sub>'))
                                    ->badge(),
                                    Infolists\Components\TextEntry::make('dedgemax')
                                    ->label(fn() => new HtmlString('e<sub>max</sub>'))
                                    ->badge(),
                                    Infolists\Components\TextEntry::make('dedgeavg')
                                    ->label(fn() => new HtmlString('e<sub>avg</sub>'))
                                    ->badge(),
                                ]),
                            ])
                        ]),
                        Components\Section::make()
                            ->schema([
                                Infolists\Components\TextEntry::make('')->default('README.md')->columnSpanFull(),
                                ViewEntry::make('description')->view('filament.infolists.markdown')
                            ])
                        ]),
                    Tabs\Tab::make('Data Exploration')
                        ->schema([
                            Infolists\Components\TextEntry::make('')->default('Node degree distribution')->columnSpanFull(),
                            ViewEntry::make('dnodes')->view('filament.infolists.chart-line-nodes')->columnSpanFull(),
                            Infolists\Components\TextEntry::make('')->default('Node degree distribution log log scale')->columnSpanFull(),
                            ViewEntry::make('dnodeshist')->view('filament.infolists.chart-scatter')->columnSpanFull(),
                            Infolists\Components\TextEntry::make('')->default('Hedges size distribution')->columnSpanFull(),
                            ViewEntry::make('dedges')->view('filament.infolists.chart-line-edges')->columnSpanFull(),
                            
                        ])
                    // Tabs\Tab::make('Download')
                    //     ->schema([
                    //         Infolists\Components\TextEntry::make('name')
                    //     ]),
                   
                ])
               
                // Infolists\Components\TextEntry::make('email'),
                // Infolists\Components\TextEntry::make('notes')
                //     ->columnSpanFull(),
            ]);
    }
    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('name')
                    ->searchable(),
                Tables\Columns\TextColumn::make('author')
                    ->searchable(),
                Tables\Columns\TextColumn::make('summary')
                    ->searchable()
                    ->toggleable(isToggledHiddenByDefault: true),
                Tables\Columns\TextColumn::make('domain')
                    ->label('Category')
                    ->searchable()
                    ->toggleable(),
                Tables\Columns\TextColumn::make('categories.type')->label('Type')
                    ->badge()
                    ->searchable(),
                Tables\Columns\TextColumn::make('nodes')
                    ->numeric()
                    ->label('|V|')
                    ->searchable()
                    ->sortable(),
                Tables\Columns\TextColumn::make('edges')
                    ->numeric()
                    ->label('|E|')
                    ->searchable()
                    ->sortable(),
                Tables\Columns\TextColumn::make('dnodemax')
                    ->numeric()
                    ->label(fn() => new HtmlString('d<sub>max</sub>'))
                    ->searchable()
                    ->sortable(),
                Tables\Columns\TextColumn::make('dedgemax')
                    ->numeric()
                    ->label(fn() => new HtmlString('e<sub>max</sub>'))
                    ->searchable()
                    ->sortable(),
                Tables\Columns\TextColumn::make('dnodeavg')
                    ->numeric()
                    ->label(fn() => new HtmlString('d<sub>avg</sub>'))
                    ->searchable()
                    ->sortable(),
                Tables\Columns\TextColumn::make('dedgeavg')
                    ->numeric()
                    ->label(fn() => new HtmlString('e<sub>avg</sub>'))
                    ->searchable()
                    ->sortable(),
                Tables\Columns\TextColumn::make('created_at')
                    ->dateTime()
                    ->label('Created At')
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
                Tables\Columns\TextColumn::make('updated_at')
                    ->dateTime()
                    ->label('Updated At')
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
            ])
            ->groups([
                'author'
            ])
            ->defaultSort('name', 'asc')
            ->filters([
                SelectFilter::make('categories')
                ->multiple()
                ->relationship('categories', 'type')
                ->preload()
                ->label('Hgraph Category')
                ->searchable(),
                Filter::make('nodes')
                ->form([
                    TextInput::make('nodes2')
                    ->numeric()
                    ->label('Min |V|'),
                ])
                ->query(function (Builder $query, array $data): Builder {
                    return $query
                        ->when(
                            $data['nodes2'],
                            fn (Builder $query, $n): Builder => $query->where('nodes', '>=', $n),
                        );
                }),
                Filter::make('edges')
                ->form([
                    TextInput::make('edges2')
                    ->numeric()
                    ->label('Min |E|'),
                ])
                ->query(function (Builder $query, array $data): Builder {
                    return $query
                        ->when(
                            $data['edges2'],
                            fn (Builder $query, $n): Builder => $query->where('edges', '>=', $n),
                        );
                })
            ])
            ->actions([
                ViewAction::make(),
               // EditAction::make(),
                Tables\Actions\Action::make('download')
                                ->label(
                                    fn ($record):string => 'Download ('.round(filesize(storage_path('/app/public/datasets/'.$record->name.'/'.$record->name.'.hgf'))/1000000, 2).' MB)'
                                )
                                ->icon('heroicon-o-arrow-down-tray')
                                ->color('success')
                                ->action(function ($record, Tables\Actions\Action $action) {
                                    redirect()->to($record->url);
                                })
            ])
            ->bulkActions([
                // Tables\Actions\BulkActionGroup::make([
                //     Tables\Actions\DeleteBulkAction::make(),
                // ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListHgraphs::route('/'),
            // 'create' => Pages\CreateHgraph::route('/create'),
            //'edit' => Pages\EditHgraph::route('/{record}/edit'),
            'view' => Pages\ViewHgraph::route('/{record}'),
        ];
    }
}
