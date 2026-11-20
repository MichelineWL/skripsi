# Domain Model — Document Continuity Assistant (DCA)

## 1. Purpose

Domain model ini mendefinisikan entitas utama dan hubungan konseptual dalam Document Continuity Assistant (DCA). Model digunakan sebagai dasar untuk merancang struktur penyimpanan data yang mendukung knowledge continuity, document retrieval, evidence traceability, dan knowledge elicitation dalam proses pergantian kepengurusan organisasi mahasiswa.

Model ini masih bersifat draft dan belum menjadi skema database final.

## 2. Entities

### Organization
Merepresentasikan organisasi mahasiswa yang menggunakan sistem DCA. Organisasi menjadi konteks utama yang membatasi kepemilikan dokumen, program, dan pengetahuan.

### Period
Merepresentasikan periode kepengurusan organisasi. Periode digunakan untuk membedakan konteks pengetahuan antar kepengurusan.

### Division
Merepresentasikan divisi atau departemen dalam organisasi. Divisi membantu mengelompokkan program, tanggung jawab, dan dokumen berdasarkan struktur organisasi.

### Program
Merepresentasikan program kerja, kegiatan, atau aktivitas organisasi. Program dapat berlangsung dalam periode tertentu dan berkaitan dengan divisi yang bertanggung jawab.

### Document
Merepresentasikan dokumen yang diunggah ke sistem, seperti proposal, laporan pertanggungjawaban, SOP, atau panduan kegiatan. Dokumen memiliki konteks organisasi dan dapat berkaitan dengan periode, program, atau divisi.

### DocumentVersion
Merepresentasikan versi spesifik dari suatu dokumen. Entitas ini digunakan untuk mempertahankan histori perubahan dan membedakan dokumen lama dari versi yang lebih baru.

### ExtractedContent
Merepresentasikan hasil ekstraksi konten dari DocumentVersion, seperti teks yang diperoleh dari PDF atau dokumen lainnya. Hasil ekstraksi dapat ditinjau sebelum digunakan untuk retrieval.

### Chunk
Merepresentasikan bagian kecil dari ExtractedContent yang digunakan sebagai unit pemrosesan dan retrieval dalam pipeline RAG. Chunk dapat menyimpan informasi locator untuk membantu menemukan kembali bagian sumbernya.

### Evidence
Merepresentasikan potongan informasi dari sumber yang digunakan untuk mendukung jawaban atau klaim sistem. Evidence harus dapat ditelusuri kembali ke dokumen, versi, dan bagian sumber yang relevan.

### DecisionContext
Merepresentasikan konteks, pertimbangan, alasan, atau keputusan yang berkaitan dengan program atau aktivitas organisasi.

### TaskGuide
Merepresentasikan panduan pelaksanaan tugas yang membantu pengurus berikutnya memahami langkah kerja, kebutuhan, dan hal-hal yang perlu diperhatikan dalam menjalankan suatu aktivitas.

### LessonLearned
Merepresentasikan pembelajaran, pengalaman, kendala, atau rekomendasi yang diperoleh dari pelaksanaan program atau aktivitas sebelumnya.

### KnowledgeInterview
Merepresentasikan sesi elicitation pengetahuan tambahan yang dilakukan sistem berdasarkan konteks dokumen atau aktivitas tertentu.

### FollowUpQuestion
Merepresentasikan pertanyaan lanjutan yang dihasilkan sistem untuk menggali informasi kontekstual atau pengalaman yang belum tercakup dalam dokumen.

### KnowledgeAnswer
Merepresentasikan jawaban atau informasi tambahan yang diberikan oleh kontributor untuk melengkapi pengetahuan yang tersedia.

## 3. Conceptual Relationships

- Organization memiliki satu atau lebih Period.
- Organization memiliki Division dan Program.
- Program berkaitan dengan Period dan Division yang bertanggung jawab.
- Document dimiliki oleh Organization dan dapat dikaitkan dengan Period, Program, dan Division.
- Document memiliki satu atau lebih DocumentVersion.
- DocumentVersion menghasilkan ExtractedContent.
- ExtractedContent diproses menjadi Chunk untuk retrieval.
- Chunk dapat digunakan sebagai sumber Evidence.
- Evidence harus dapat ditelusuri kembali ke Chunk dan DocumentVersion asal.
- Document atau DocumentVersion dapat memicu KnowledgeInterview.
- KnowledgeInterview terdiri dari FollowUpQuestion.
- FollowUpQuestion dapat menerima KnowledgeAnswer.
- KnowledgeAnswer dapat melengkapi konteks dari dokumen atau program terkait.
- DecisionContext berkaitan dengan program atau aktivitas dan dapat didukung oleh dokumen.
- TaskGuide dapat berkaitan dengan Program dan merujuk pada dokumen yang relevan.
- LessonLearned berkaitan dengan Program atau aktivitas dan dapat didukung oleh dokumen maupun KnowledgeAnswer.

## 4. Context and Provenance

Sistem perlu mempertahankan konteks organisasi, periode, program, dan divisi agar retrieval tidak mencampurkan informasi dari aktivitas atau kepengurusan yang berbeda secara tidak relevan.

Setiap informasi yang digunakan dalam jawaban perlu memiliki provenance yang memungkinkan penelusuran kembali ke sumber asalnya. Untuk dokumen, provenance mencakup Document, DocumentVersion, ExtractedContent, dan Chunk yang relevan.

KnowledgeAnswer yang berasal dari knowledge elicitation juga perlu mempertahankan konteks sesi, pertanyaan, kontributor, serta sumber atau aktivitas yang melatarbelakanginya.

## 5. Model Status

Beberapa entitas nantinya memerlukan status untuk mendukung proses sistem, misalnya:

- DocumentVersion: uploaded, extracted, reviewed, indexed, failed.
- KnowledgeAnswer: pending_review, confirmed, rejected.
- KnowledgeInterview: active, completed, cancelled.

Daftar status tersebut masih berupa kandidat dan akan disesuaikan dengan requirement serta workflow implementasi.

## 6. Validation Note

Domain model ini masih merupakan draft konseptual. Relasi dan atribut setiap entitas akan divalidasi terhadap requirement hasil analisis penelitian, khususnya kebutuhan contextual retrieval, document versioning, provenance, knowledge elicitation, dan knowledge continuity, sebelum ditetapkan menjadi skema database dan implementasi ORM/migration.

erDiagram
    ORGANIZATION ||--o{ PERIOD : has
    ORGANIZATION ||--o{ DIVISION : has
    ORGANIZATION ||--o{ PROGRAM : runs
    ORGANIZATION ||--o{ DOCUMENT : owns

    PERIOD ||--o{ PROGRAM : includes
    DIVISION ||--o{ PROGRAM : responsible_for

    PERIOD o|--o{ DOCUMENT : contextualizes
    PROGRAM o|--o{ DOCUMENT : relates_to
    DIVISION o|--o{ DOCUMENT : categorized_by

    DOCUMENT ||--|{ DOCUMENT_VERSION : has
    DOCUMENT_VERSION ||--o{ EXTRACTED_CONTENT : produces
    EXTRACTED_CONTENT ||--o{ CHUNK : split_into
    CHUNK ||--o{ EVIDENCE : supports

    DOCUMENT_VERSION o|--o| KNOWLEDGE_INTERVIEW : may_trigger
    KNOWLEDGE_INTERVIEW ||--o{ FOLLOW_UP_QUESTION : asks
    FOLLOW_UP_QUESTION ||--o| KNOWLEDGE_ANSWER : receives

    PROGRAM ||--o{ DECISION_CONTEXT : has
    DOCUMENT o|--o{ DECISION_CONTEXT : supports

    PROGRAM ||--o{ TASK_GUIDE : has
    DOCUMENT o|--o{ TASK_GUIDE : references

    PROGRAM ||--o{ LESSON_LEARNED : produces
    DOCUMENT o|--o{ LESSON_LEARNED : supports
    KNOWLEDGE_ANSWER o|--o{ LESSON_LEARNED : contributes