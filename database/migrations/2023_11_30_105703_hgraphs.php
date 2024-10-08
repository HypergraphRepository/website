<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('hgraphs', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->string('name');
            $table->string('domain')->nullable();
            $table->string('category')->nullable();
            $table->string('author')->nullable();
            $table->string('authorurl')->nullable();
            $table->string('url')->nullable();
            $table->longText('description')->nullable();
            $table->longText('summary')->nullable();
            $table->integer('nodes')->unsigned()->nullable();
            $table->integer('edges')->unsigned()->nullable();
            $table->integer('dnodemax')->unsigned()->nullable();
            $table->integer('dedgemax')->unsigned()->nullable();
            $table->float('dnodeavg')->unsigned()->nullable();
            $table->float('dedgeavg')->unsigned()->nullable();
            $table->longText('dnodes')->nullable();
            $table->longText('dedges')->nullable();
            $table->longText('dnodeshist')->nullable();
            $table->longText('dedgeshist')->nullable();
            $table->longText('motifsdist')->unsigned()->nullable();
            $table->float('dnodemedian')->unsigned()->nullable();
            $table->float('dedgemedian')->unsigned()->nullable();
            $table->integer('downloads')->unsigned()->default(0);
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        //
    }
};
