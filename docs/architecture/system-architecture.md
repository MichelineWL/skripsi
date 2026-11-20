# System Architecture — Document Continuity Assistant (DCA)

## 1. Purpose

Dokumen ini menjelaskan arsitektur konseptual Document Continuity Assistant (DCA), termasuk komponen utama, tanggung jawab masing-masing komponen, serta alur pemrosesan dokumen dan pencarian pengetahuan.

Arsitektur dirancang untuk mendukung document retrieval, contextual knowledge retrieval, evidence traceability, dan knowledge elicitation dalam konteks pergantian kepengurusan organisasi mahasiswa.

## 2. Architecture Overview

DCA dirancang menggunakan modular architecture dengan satu backend application yang menyediakan API untuk frontend. Backend terdiri atas beberapa service yang memiliki tanggung jawab berbeda, sementara penyimpanan data utama dan vector index dipisahkan sesuai fungsinya.

Komponen utama meliputi:

- Frontend Interface
- FastAPI Backend / API
- Document Service
- Retrieval and Answer Service
- Knowledge Elicitation Service
- Organization and Context Service
- Document Processing Pipeline
- Database
- Document Storage
- Vector Index
- External AI Providers

## 3. Component Responsibilities

### Frontend Interface
Menyediakan antarmuka untuk upload dokumen, pemilihan konteks organisasi, pengajuan pertanyaan, melihat jawaban dan evidence, serta memberikan informasi tambahan melalui knowledge elicitation.

### FastAPI Backend / API
Menangani request dari frontend, validasi input, koordinasi service, dan pengiriman response.

### Document Service
Mengelola dokumen, metadata, document versions, serta workflow pemrosesan dokumen.

### Document Processing Pipeline
Melakukan ekstraksi konten, review hasil ekstraksi, chunking, embedding, dan indexing.

### Retrieval and Answer Service
Mengelola pencarian informasi berdasarkan query dan konteks, pemilihan evidence, serta penyusunan jawaban dengan bantuan LLM.

### Knowledge Elicitation Service
Menghasilkan pertanyaan kontekstual berdasarkan dokumen atau aktivitas tertentu dan mengelola jawaban tambahan dari kontributor.

### Organization and Context Service
Mengelola konteks organisasi, periode kepengurusan, divisi, dan program yang digunakan untuk membatasi dan mengarahkan retrieval.

### Database
Menyimpan metadata, konteks organisasi, dokumen, versi dokumen, hasil ekstraksi, serta data knowledge elicitation. Database utama direncanakan menggunakan SQLite untuk prototype.

### Document Storage
Menyimpan file dokumen asli dan file pendukung pemrosesan.

### Vector Index
Menyimpan embeddings dan metadata retrieval untuk mendukung pencarian semantik. Vector index direncanakan menggunakan Qdrant dan bersifat derived data yang dapat dibangun ulang dari sumber yang tersimpan.

### External AI Providers
Menyediakan model untuk embedding dan generasi jawaban. Penggunaan provider dilakukan melalui adapter/service sehingga komponen aplikasi tidak bergantung langsung pada implementasi provider tertentu.

## 4. Document Ingestion Workflow

1. Pengguna mengunggah dokumen melalui frontend.
2. API memvalidasi request dan meneruskannya ke Document Service.
3. Sistem menyimpan file asli dan metadata dokumen.
4. Document Processing Pipeline melakukan ekstraksi konten.
5. Hasil ekstraksi disimpan dan dapat ditinjau.
6. Konten yang disetujui diproses menjadi chunks.
7. Chunk diubah menjadi embeddings.
8. Embeddings dan metadata retrieval disimpan ke vector index.
9. Dokumen menjadi tersedia untuk retrieval berdasarkan konteks yang sesuai.

## 5. Query and Retrieval Workflow

1. Pengguna mengajukan pertanyaan melalui frontend.
2. API meneruskan request ke Retrieval and Answer Service.
3. Sistem menentukan konteks pencarian yang relevan.
4. Sistem membatasi kandidat informasi berdasarkan konteks organisasi, periode, program, atau divisi.
5. Sistem melakukan retrieval terhadap vector index.
6. Sistem memilih evidence yang relevan.
7. LLM menyusun jawaban berdasarkan evidence yang tersedia.
8. Sistem mengembalikan jawaban beserta citation dan informasi sumber.
9. Jika evidence tidak memadai, sistem perlu menyatakan keterbatasan informasi.

## 6. Knowledge Elicitation Workflow

1. Dokumen yang telah diproses dapat menjadi dasar knowledge elicitation.
2. Knowledge Elicitation Service menganalisis konteks dokumen untuk mengidentifikasi informasi yang berpotensi belum tercakup.
3. Sistem menghasilkan pertanyaan lanjutan yang relevan.
4. Kontributor memberikan jawaban atau informasi tambahan.
5. Jawaban dapat melalui proses review atau confirmation.
6. Informasi yang dikonfirmasi disimpan dengan provenance dan konteks.
7. Informasi tersebut dapat diproses agar tersedia untuk retrieval.

## 7. Data Storage Strategy

SQLite digunakan sebagai authoritative data store untuk metadata dan data utama sistem.

Document Storage digunakan untuk menyimpan file asli.

Qdrant digunakan sebagai derived vector index untuk pencarian semantik. Data di vector index harus memiliki referensi ke sumber dan konteks asalnya agar retrieval tetap dapat ditelusuri dan dibatasi.

## 8. Architectural Considerations

- Sistem menggunakan modular architecture untuk memisahkan tanggung jawab tanpa memerlukan deployment microservices.
- Retrieval harus mempertimbangkan konteks organisasi dan periode untuk mengurangi cross-context retrieval.
- Jawaban sistem harus didukung evidence yang dapat ditelusuri.
- File asli dan metadata sumber harus dipertahankan.
- Vector index dapat dibangun ulang dari sumber data yang tersimpan.
- Knowledge elicitation bersifat kontekstual dan informasi tambahan perlu mempertahankan provenance.
- Kompleksitas implementasi disesuaikan dengan kebutuhan prototype dan evaluasi penelitian.

## 9. Validation Note

Arsitektur ini merupakan rancangan awal yang akan divalidasi terhadap requirement penelitian, domain model, serta kebutuhan implementasi dan evaluasi prototype DCA.

flowchart TD
    U[User / Pengurus Organisasi]

    U --> UI[Frontend Web Interface]

    UI --> API[FastAPI Backend / API]

    API --> S1[Document Service]
    API --> S2[Retrieval & Answer Service]
    API --> S3[Knowledge Elicitation Service]
    API --> S4[Organization & Context Service]

    S1 --> EX[Document Extraction & Processing]
    EX --> CH[Chunking]
    CH --> IDX[Embedding & Indexing]

    S2 --> RET[Context Filtering & Retrieval]
    RET --> EV[Evidence Selection]
    EV --> LLM[LLM Answer Generation]

    S3 --> QE[Follow-up Question Generation]
    QE --> KA[Knowledge Answer Processing]
    KA --> CH

    S1 --> DB[(SQLite Database)]
    S2 --> DB
    S3 --> DB
    S4 --> DB

    S1 --> FS[(Document Storage)]
    EX --> FS

    IDX --> VDB[(Qdrant Vector Index)]
    RET --> VDB

    LLM --> API
    EV --> API
    API --> UI