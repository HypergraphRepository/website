<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "api" middleware group. Make something great!
|
*/

Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
    return $request->user();
});

Route::get('/hello', function () { # link/api/hello
    return response()->json(['message' => 'Hello World!'], 200);
});

# api to download a file with a specific name #/api/download/hif/{name} or /api/download/hgf/{name}
Route::get('/download/{format}/{name}', function ($format, $name) {
    // Print name and format for debug
    
    if (!in_array($format = strtolower($format), ['hif', 'hgf'])) {
        return response()->json(['message' => 'Invalid format!'], 400);
    }

    if ($format === 'hif') {
        $format = 'json';
    } elseif ($format === 'hgf') {
        $format = 'hgf';
    }

    $path = storage_path('/app/public/datasets/' . $name . '/' . $name . '.' . $format);
    if (!file_exists($path)) {
        return response()->json(['message' => 'File not found!'], 404);
    }
    return response()->download($path);
});

Route::get('/hif/{name}', function ($name) {
    $path = storage_path('/app/public/datasets/' . $name . '/' . $name . '.json');
    if (!file_exists($path)) {
        return response()->json(['message' => 'File not found! Or it was too large! Check The compressed files!'], 404);
    }
    $content = file_get_contents($path);
    return response($content, 200)->header('Content-Type', 'application/json');
});