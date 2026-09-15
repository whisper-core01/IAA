default:
    @just --list

check:
    cargo fmt --all -- --check
    cargo clippy --workspace --all-targets --all-features -- -D warnings
    cargo test --workspace --all-features

tree:
    find . -maxdepth 4 -type d | sort

