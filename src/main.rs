use std::env;

use axum::{Router, body::Bytes, extract::State, routing::post};
use axum_streams::StreamBodyAs;
use tower_http::{
    cors::{Any, CorsLayer},
    services::{ServeDir, ServeFile},
};

use axum::response::IntoResponse;
use futures::stream;
use llama_cpp::standard_sampler::StandardSampler;
use llama_cpp::{LlamaModel, LlamaParams, SessionParams};

#[derive(Clone)]
struct AppState {
    model: LlamaModel,
}

#[tokio::main]
async fn main() {
    env_logger::init();
    log::info!("Starting llama-cpp-rs server");

    let port = env::var("PORT").unwrap_or_else(|_| "8080".to_string());

    // Create a model from anything that implements `AsRef<Path>`:
    let model = LlamaModel::load_from_file_async("model.bin", LlamaParams::default())
        .await
        .expect("Failed to load model");

    let state = AppState { model };

    let app = Router::new()
        .route("/prompt", post(run_prompt))
        .nest_service("/openapi.yaml", ServeDir::new("./static"))
        .fallback_service(ServeFile::new("./templates/index.html"))
        .layer(CorsLayer::new().allow_origin(Any))
        .with_state(state);

    let listener = tokio::net::TcpListener::bind(format!("0.0.0.0:{port}"))
        .await
        .unwrap_or_else(|_| panic!("Failed to bind to port \"{port}\""));

    log::info!("Listening on port {port}");
    axum::serve(listener, app).await.unwrap();
}

async fn run_prompt(State(state): State<AppState>, prompt: Bytes) -> impl IntoResponse {
    let mut session = state
        .model
        .create_session(SessionParams::default())
        .expect("Failed to create session");

    session.advance_context_async(prompt).await.unwrap();

    let completions = session
        .start_completing_with(StandardSampler::default(), 1024)
        .expect("Failed to start completing")
        .into_strings();

    let stream = stream::iter(completions);

    StreamBodyAs::text(stream)
}
