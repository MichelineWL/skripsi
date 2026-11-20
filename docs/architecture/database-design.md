# Database Design — Document Continuity Assistant (DCA)

## 1. Purpose

Dokumen ini mendefinisikan rancangan awal struktur database DCA berdasarkan domain model dan system architecture. Rancangan mendukung pengelolaan konteks organisasi, dokumen dan versi, pemrosesan konten, retrieval, evidence traceability, serta knowledge elicitation.

Database design ini merupakan logical design awal dan belum menjadi implementasi physical database.

## 2. Database Strategy

- SQLite digunakan sebagai authoritative data store.
- Qdrant digunakan sebagai derived vector index untuk semantic retrieval.
- File dokumen asli disimpan di document storage.
- Metadata dan relasi sumber disimpan di SQLite.
- Vector index dapat dibangun ulang berdasarkan data sumber yang tersimpan.

## 3. Proposed Tables

### 3.1 Organization and Context

#### organizations
Menyimpan identitas organisasi.

- id (PK)
- name

#### periods
Menyimpan periode kepengurusan.

- id (PK)
- organization_id (FK)
- name
- start_date
- end_date

#### divisions
Menyimpan divisi atau departemen dalam konteks organisasi dan periode.

- id (PK)
- organization_id (FK)
- period_id (FK)
- name

#### programs
Menyimpan program kerja atau aktivitas organisasi.

- id (PK)
- organization_id (FK)
- period_id (FK)
- division_id (FK)
- name
- description
- status

### 3.2 Document Management

#### documents
Menyimpan identitas dan konteks dokumen.

- id (PK)
- organization_id (FK)
- period_id (FK, nullable)
- program_id (FK, nullable)
- division_id (FK, nullable)
- title
- document_type

#### document_versions
Menyimpan versi file dokumen.

- id (PK)
- document_id (FK)
- version_number
- file_path
- file_hash
- uploaded_at
- processing_status

### 3.3 Document Processing and Retrieval

#### extracted_contents
Menyimpan hasil ekstraksi konten dari document version.

- id (PK)
- document_version_id (FK)
- extraction_method
- content
- extraction_status
- created_at

#### chunks
Menyimpan bagian konten yang digunakan untuk retrieval.

- id (PK)
- extracted_content_id (FK)
- document_version_id (FK)
- chunk_index
- content
- page_number (nullable)
- locator
- vector_id (nullable)

Chunk mempertahankan referensi terhadap extracted content dan document version asal untuk mendukung provenance dan citation.

### 3.4 Knowledge Elicitation

#### knowledge_interviews
Menyimpan sesi knowledge elicitation yang berkaitan dengan dokumen tertentu.

- id (PK)
- document_version_id (FK)
- status
- created_at

#### follow_up_questions
Menyimpan pertanyaan kontekstual yang dihasilkan sistem.

- id (PK)
- knowledge_interview_id (FK)
- question_text
- question_order
- status

#### knowledge_answers
Menyimpan jawaban tambahan dari kontributor.

- id (PK)
- follow_up_question_id (FK)
- answer_text
- contributor (nullable)
- review_status
- created_at

### 3.5 Knowledge Continuity

#### decision_contexts
Menyimpan konteks dan alasan keputusan.

- id (PK)
- program_id (FK)
- description
- document_id (FK, nullable)

#### task_guides
Menyimpan panduan pelaksanaan tugas.

- id (PK)
- program_id (FK)
- title
- content

#### lessons_learned
Menyimpan pengalaman dan pembelajaran dari aktivitas sebelumnya.

- id (PK)
- program_id (FK)
- description
- document_id (FK, nullable)
- knowledge_answer_id (FK, nullable)

## 4. Relationship Summary

- Organization memiliki Period, Division, Program, dan Document.
- Period berkaitan dengan Program, Division, dan Document.
- Division bertanggung jawab terhadap Program.
- Program dapat memiliki Document, DecisionContext, TaskGuide, dan LessonLearned.
- Document memiliki DocumentVersion.
- DocumentVersion menghasilkan ExtractedContent.
- ExtractedContent diproses menjadi Chunk.
- Chunk dapat digunakan sebagai Evidence untuk jawaban.
- DocumentVersion dapat memicu KnowledgeInterview.
- KnowledgeInterview memiliki FollowUpQuestion.
- FollowUpQuestion dapat menerima KnowledgeAnswer.
- KnowledgeAnswer dapat digunakan untuk melengkapi LessonLearned.

## 5. Context Isolation

Data yang memiliki konteks organisasi, periode, program, atau divisi harus mempertahankan relasi konteksnya.

Retrieval tidak boleh hanya bergantung pada semantic similarity. Sistem perlu mempertimbangkan context metadata untuk membatasi informasi yang dapat digunakan dalam jawaban.

Konteks yang tidak diketahui atau tidak ditentukan tidak boleh secara otomatis dianggap sama dengan konteks yang dipilih pengguna.

## 6. Provenance

Setiap Chunk harus dapat ditelusuri kembali ke:

- ExtractedContent
- DocumentVersion
- Document

Evidence yang digunakan dalam jawaban merujuk pada Chunk atau sumber spesifik beserta informasi locator yang diperlukan.

KnowledgeAnswer harus mempertahankan relasi terhadap pertanyaan, sesi knowledge elicitation, serta konteks dokumen yang melatarbelakanginya.

## 7. Design Decisions and Limitations

- Evidence belum dirancang sebagai tabel tersendiri pada MVP. Evidence dapat direpresentasikan sebagai runtime reference ke Chunk beserta citation metadata.
- Vector index merupakan derived data dan bukan authoritative source.
- Struktur tabel dan atribut masih merupakan rancangan awal.
- Tipe data, constraint, indexing strategy, dan migration belum ditentukan.
- Struktur akan disesuaikan berdasarkan requirement, implementasi, dan evaluasi prototype.

## 8. Validation Note

Logical database design ini masih merupakan draft. Struktur dan relasi akan divalidasi terhadap requirement penelitian dan workflow prototype sebelum diterjemahkan menjadi ORM models dan database migrations.