use std::env;
use std::path::PathBuf;

use axum::{Router, body::Body, extract::State, routing::post};
use kalosm::language::*;
use tokio::time::Instant;
use tower_http::{
    cors::{Any, CorsLayer},
    services::{ServeDir, ServeFile},
};

use axum::response::IntoResponse;
#[derive(Clone)]
struct AppState {
    model: Llama,
}

#[tokio::main]
async fn main() {
    let port = env::var("PORT").unwrap_or_else(|_| "8080".to_string());

    println!("Loading model...");

    let start = Instant::now();

    let model = Llama::builder()
        .with_source(
            LlamaSource::new(FileSource::Local(PathBuf::from("model.gguf")))
                .with_tokenizer(FileSource::Local(PathBuf::from("tokenizer.json"))),
        )
        .build()
        .await
        .unwrap();

    println!("Finished loading model. Took: {:?}", start.elapsed());

    let state = AppState { model };

    let app = Router::new()
        .route("/prompt", post(run_prompt))
        .nest_service("/static", ServeDir::new("./static"))
        .fallback_service(ServeFile::new("./templates/index.html"))
        .layer(CorsLayer::new().allow_origin(Any))
        .with_state(state);

    let listener = tokio::net::TcpListener::bind(format!("0.0.0.0:{port}"))
        .await
        .unwrap_or_else(|_| panic!("Failed to bind to port \"{port}\""));

    println!("Listening on port {}", port);
    axum::serve(listener, app).await.unwrap();
}

async fn run_prompt(State(state): State<AppState>, prompt: String) -> impl IntoResponse {
    println!("Received prompt: {}", prompt);

    let model = state.model;
    // .chat()
    // .with_system_prompt("You are Socrates, a wise philosopher.");

    println!("Created a chat instance");

    let response_stream = model(&prompt);

    println!("Response stream created, streaming response...");

    fn infallible(t: String) -> Result<String, std::convert::Infallible> {
        Ok(t)
    }

    Body::from_stream(response_stream.map(infallible))
}
