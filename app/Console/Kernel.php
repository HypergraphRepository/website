<?php

namespace App\Console;

use Illuminate\Console\Scheduling\Schedule;
use Illuminate\Foundation\Console\Kernel as ConsoleKernel;

class Kernel extends ConsoleKernel
{
    /**
     * Define the application's command schedule.
     */
    protected function schedule(Schedule $schedule): void
    {
        $schedule->exec('bash ./scripts/gitPull.sh')
            ->everyFiveMinutes()
            ->sendOutputTo(storage_path('logs/gitPull.log'));
        $schedule->exec('python3 ./scripts/updateDB.py')
            ->everyTenMinutes()
            ->withoutOverlapping(20)
            ->appendOutputTo(storage_path('logs/updateDB.log'));
        $schedule->exec('python3 ./scripts/motifs.py')
            ->daily()
            ->withoutOverlapping(20)
            // ->sendOutputTo(storage_path('logs/motifs.log'));
            ->appendOutputTo(storage_path('logs/motifs2.log'));
    }

    /**
     * Register the commands for the application.
     */
    protected function commands(): void
    {
        $this->load(__DIR__.'/Commands');

        require base_path('routes/console.php');
    }
}
