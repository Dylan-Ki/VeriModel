// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;

// Command để check backend health

#[tauri::command]
async fn check_backend_health() -> Result<bool, String> {
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(2))
        .build()
        .map_err(|e| e.to_string())?;
        
    match client
        .get("http://localhost:8000/api/v1/health")
        .send()
        .await
    {
        Ok(response) => Ok(response.status().is_success()),
        Err(_) => Ok(false),
    }
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            check_backend_health
        ])
        .setup(|app| {
            // Check if backend is running on startup
            let app_handle = app.handle();
            
            tauri::async_runtime::spawn(async move {
                // Wait a bit for the backend to potentially start
                tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
                
                // Check backend health
                if let Ok(is_healthy) = check_backend_health().await {
                    if !is_healthy {
                        eprintln!("⚠️ Backend server not detected at http://localhost:8000");
                        eprintln!("⚠️ Please start the backend with: python run_api.py");
                    }
                }
            });
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

