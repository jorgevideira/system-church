#!/usr/bin/env python3
"""
Direct SQL execution to create missing tables
This bypasses the migration conflict
"""
import sqlite3
from pathlib import Path

# Database file
db_file = Path("/root/system-church/backend/church_finance.db").resolve()
print(f"Database: {db_file}")
print(f"Exists: {db_file.exists()}")

conn = sqlite3.connect(str(db_file))
cursor = conn.cursor()

# Check if tables already exist
print("\nChecking if tables exist...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bible_school_students'")
students_exists = cursor.fetchone() is not None
print(f"bible_school_students exists: {students_exists}")

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bible_school_attendance'")
attendance_exists = cursor.fetchone() is not None
print(f"bible_school_attendance exists: {attendance_exists}")

if not students_exists:
    print("\nCreating bible_school_students table...")
    cursor.execute("""
    CREATE TABLE bible_school_students (
        id INTEGER NOT NULL,
        class_id INTEGER NOT NULL,
        name VARCHAR(255) NOT NULL,
        contact VARCHAR(255),
        email VARCHAR(255),
        birth_date DATE,
        active BOOLEAN NOT NULL DEFAULT 1,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(class_id) REFERENCES bible_school_classes (id) ON DELETE CASCADE
    );
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX ix_bible_school_students_class_id ON bible_school_students (class_id)")
    cursor.execute("CREATE INDEX ix_bible_school_students_name ON bible_school_students (name)")
    cursor.execute("CREATE INDEX ix_bible_school_students_active ON bible_school_students (active)")
    print("✓ Created bible_school_students table")
else:
    print("✓ bible_school_students table already exists")

if not attendance_exists:
    print("\nCreating bible_school_attendance table...")
    cursor.execute("""
    CREATE TABLE bible_school_attendance (
        id INTEGER NOT NULL,
        lesson_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'pending',
        notes VARCHAR(255),
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(lesson_id) REFERENCES bible_school_lessons (id) ON DELETE CASCADE,
        FOREIGN KEY(student_id) REFERENCES bible_school_students (id) ON DELETE CASCADE,
        UNIQUE(lesson_id, student_id)
    );
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX ix_bible_school_attendance_lesson_id ON bible_school_attendance (lesson_id)")
    cursor.execute("CREATE INDEX ix_bible_school_attendance_student_id ON bible_school_attendance (student_id)")
    cursor.execute("CREATE INDEX ix_bible_school_attendance_status ON bible_school_attendance (status)")
    print("✓ Created bible_school_attendance table")
else:
    print("✓ bible_school_attendance table already exists")

# Commit changes
conn.commit()
conn.close()

print("\n✓ Database tables created successfully!")
