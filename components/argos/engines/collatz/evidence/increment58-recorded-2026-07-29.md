# Trace historique increment58 — 2026-07-29

> **Cette trace ne prouve pas la conjecture de Collatz.**
>
> Elle est publiée comme transcription d'une exécution antérieure fournie par
> l'auteur. L'archive source increment58 n'ayant pas été retrouvée sous une
> forme récupérable lors de cette publication, cette trace n'a pas été
> reproduite dans l'environnement de validation actuel.

Archive mentionnée :

```text
whisper_job_engine_increment58_real_gpu_workspace_million_publication_stress_unverified_2026-07-29.zip
```

Sorties enregistrées :

```text
COLLATZ_REAL_GPU_WORKSPACE_PASS cells=1000000 dims=100x100x100 gpu_elapsed_ms=5 cpu_replay_elapsed_ms=8632 workspace_hash=38023d1376ed24d5e31299823e383b8f0a7aa3d62636ee35cfd6403a8bc6600f gpu_authority=DENIED cpu_replay=EXACT
COLLATZ_REAL_GPU_WORKSPACE_ADMISSION_PASS workspace_hash=38023d1376ed24d5e31299823e383b8f0a7aa3d62636ee35cfd6403a8bc6600f admission_hash=cd5be3477c2a5c2461b8ef30a0b7827086545b9bf7c75609ba735c612a054700 wal_records=1 wal_bytes=465 gpu_authority=DENIED cpu_replay=EXACT replay_status=EXACT
COLLATZ_REAL_GPU_WORKSPACE_PUBLICATION_PASS workspace_hash=38023d1376ed24d5e31299823e383b8f0a7aa3d62636ee35cfd6403a8bc6600f admission_hash=cd5be3477c2a5c2461b8ef30a0b7827086545b9bf7c75609ba735c612a054700 publication_hash=f7c298cdeabe85338ba2d9964080f1ae66f0000abc3990f8bc11483b94f3f2f7 publication_wal_records=1 publication_wal_bytes=551 authority=WHISPER_CANONICAL_WAL replay_status=EXACT
COLLATZ_REAL_GPU_WORKSPACE_PUBLICATION_STRESS_PASS iterations=10000000 workspace_hash=38023d1376ed24d5e31299823e383b8f0a7aa3d62636ee35cfd6403a8bc6600f admission_hash=cd5be3477c2a5c2461b8ef30a0b7827086545b9bf7c75609ba735c612a054700 publication_hash=f7c298cdeabe85338ba2d9964080f1ae66f0000abc3990f8bc11483b94f3f2f7 publication_wal_records=1 publication_wal_bytes=551 publication_wal_sha256=e8136a8d16dc93b557f3a0b961418c1fb8619597814202d059f5e7410a365b78 replay_status=EXACT elapsed_ms=7669
```

## Interprétation autorisée

La trace indique qu'à cette date, dans l'environnement de l'auteur, le pipeline
a annoncé une égalité exacte entre le résultat GPU et son rejeu CPU, puis une
stabilité des objets publiés pendant le stress-test programmé.

Elle n'établit ni l'authenticité indépendante de l'exécution, ni la correction
mathématique générale de l'algorithme, ni la vérité de la conjecture de Collatz.
`gpu_authority=DENIED` signifie précisément que le calcul GPU n'était pas
l'autorité canonique de publication.

