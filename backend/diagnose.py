#!/usr/bin/env python3
"""Diagnostic script to check database state"""
import sys
import traceback
from sqlalchemy import inspect
from app.db.session import engine
from app.db.models import (
    BibleSchoolStudent,
    BibleSchoolAttendance,
    BibleSchoolLesson,
    BibleSchoolClass,
)

print("=" * 60)
print("DIAGNÓSTICO DO BANCO DE DADOS")
print("=" * 60)

try:
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print("\n✓ Conexão com banco de dados: OK")
    print(f"\nTabelas existentes ({len(existing_tables)}):")
    for table in sorted(existing_tables):
        print(f"  - {table}")
    
    print("\nTabelasEscolaBíblica esperadas:")
    expected = [
        "bible_school_courses",
        "bible_school_classes", 
        "bible_school_professors",
        "bible_school_lessons",
        "bible_school_students",
        "bible_school_attendance",
    ]
    
    for table in expected:
        exists = table in existing_tables
        status = "✓ ENCONTRADA" if exists else "✗ FALTANDO"
        print(f"  [{status}] {table}")
    
    # Try to query each table
    print("\nTentando consultar tabelas...")
    try:
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        db = Session()
        
        student_count = db.query(BibleSchoolStudent).count()
        print(f"  ✓ BibleSchoolStudent: {student_count} registros")
        
        attendance_count = db.query(BibleSchoolAttendance).count()
        print(f"  ✓ BibleSchoolAttendance: {attendance_count} registros")
        
        lesson_count = db.query(BibleSchoolLesson).count()
        print(f"  ✓ BibleSchoolLesson: {lesson_count} registros")
        
        db.close()
        
    except Exception as e:
        print(f"  ✗ ERRO ao consultar: {e}")
        traceback.print_exc()

except Exception as e:
    print(f"\n✗ ERRO: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("FIM DO DIAGNÓSTICO")
print("=" * 60)
