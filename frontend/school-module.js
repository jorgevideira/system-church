(function () {
  const apiPrefix = "/api/v1";
  const permissionStorageKey = "currentUserPermissions";
  const isAdminStorageKey = "currentUserIsAdmin";

  const el = {
    financeBtn: document.getElementById("moduleFinanceBtn"),
    cellsBtn: document.getElementById("moduleCellsBtn"),
    schoolBtn: document.getElementById("moduleBibleSchoolBtn"),
    financeModule: document.getElementById("financeModule"),
    cellsModule: document.getElementById("cellsModule"),
    schoolModule: document.getElementById("bibleSchoolModule"),
    schoolMessage: document.getElementById("schoolMessage"),
    schoolNavCoursesBtn: document.getElementById("schoolNavCoursesBtn"),
    schoolNavClassesBtn: document.getElementById("schoolNavClassesBtn"),
    schoolNavProfessorsBtn: document.getElementById("schoolNavProfessorsBtn"),
    schoolNavLessonsBtn: document.getElementById("schoolNavLessonsBtn"),
    schoolNavStudentsBtn: document.getElementById("schoolNavStudentsBtn"),
    schoolNavAttendanceBtn: document.getElementById("schoolNavAttendanceBtn"),
    schoolNavDashboardBtn: document.getElementById("schoolNavDashboardBtn"),
    schoolCoursesView: document.getElementById("schoolCoursesView"),
    schoolClassesView: document.getElementById("schoolClassesView"),
    schoolProfessorsView: document.getElementById("schoolProfessorsView"),
    schoolLessonsView: document.getElementById("schoolLessonsView"),
    schoolStudentsView: document.getElementById("schoolStudentsView"),
    schoolAttendanceView: document.getElementById("schoolAttendanceView"),
    schoolDashboardView: document.getElementById("schoolDashboardView"),
    schoolDashboardRefreshBtn: document.getElementById("schoolDashboardRefreshBtn"),
    schoolDashboardCourseId: document.getElementById("schoolDashboardCourseId"),
    schoolDashboardClassId: document.getElementById("schoolDashboardClassId"),
    schoolDashboardMinPercentage: document.getElementById("schoolDashboardMinPercentage"),
    dashboardTotalLessons: document.getElementById("dashboardTotalLessons"),
    dashboardTotalStudents: document.getElementById("dashboardTotalStudents"),
    dashboardAvgAttendance: document.getElementById("dashboardAvgAttendance"),
    dashboardApprovedCount: document.getElementById("dashboardApprovedCount"),
    dashboardFailedCount: document.getElementById("dashboardFailedCount"),
    dashboardApprovalRate: document.getElementById("dashboardApprovalRate"),
    schoolDashboardBody: document.getElementById("schoolDashboardBody"),
    schoolCoursesRefreshBtn: document.getElementById("schoolCoursesRefreshBtn"),
    schoolClassesRefreshBtn: document.getElementById("schoolClassesRefreshBtn"),
    schoolProfessorsRefreshBtn: document.getElementById("schoolProfessorsRefreshBtn"),
    schoolLessonsRefreshBtn: document.getElementById("schoolLessonsRefreshBtn"),
    schoolStudentsRefreshBtn: document.getElementById("schoolStudentsRefreshBtn"),
    schoolAttendanceRefreshBtn: document.getElementById("schoolAttendanceRefreshBtn"),
    schoolCourseForm: document.getElementById("schoolCourseForm"),
    schoolCourseId: document.getElementById("schoolCourseId"),
    schoolCourseName: document.getElementById("schoolCourseName"),
    schoolCourseDescription: document.getElementById("schoolCourseDescription"),
    schoolCourseTotalLessons: document.getElementById("schoolCourseTotalLessons"),
    schoolCourseActive: document.getElementById("schoolCourseActive"),
    schoolCoursesBody: document.getElementById("schoolCoursesBody"),
    schoolClassForm: document.getElementById("schoolClassForm"),
    schoolClassId: document.getElementById("schoolClassId"),
    schoolClassCourseId: document.getElementById("schoolClassCourseId"),
    schoolClassName: document.getElementById("schoolClassName"),
    schoolClassWeekday: document.getElementById("schoolClassWeekday"),
    schoolClassStartTime: document.getElementById("schoolClassStartTime"),
    schoolClassEndTime: document.getElementById("schoolClassEndTime"),
    schoolClassProfessorName: document.getElementById("schoolClassProfessorName"),
    schoolClassContact: document.getElementById("schoolClassContact"),
    schoolClassActive: document.getElementById("schoolClassActive"),
    schoolClassesBody: document.getElementById("schoolClassesBody"),
    schoolProfessorForm: document.getElementById("schoolProfessorForm"),
    schoolProfessorId: document.getElementById("schoolProfessorId"),
    schoolProfessorName: document.getElementById("schoolProfessorName"),
    schoolProfessorContact: document.getElementById("schoolProfessorContact"),
    schoolProfessorEmail: document.getElementById("schoolProfessorEmail"),
    schoolProfessorBio: document.getElementById("schoolProfessorBio"),
    schoolProfessorActive: document.getElementById("schoolProfessorActive"),
    schoolProfessorsBody: document.getElementById("schoolProfessorsBody"),
    schoolLessonForm: document.getElementById("schoolLessonForm"),
    schoolLessonId: document.getElementById("schoolLessonId"),
    schoolLessonClassId: document.getElementById("schoolLessonClassId"),
    schoolLessonProfessorId: document.getElementById("schoolLessonProfessorId"),
    schoolLessonDate: document.getElementById("schoolLessonDate"),
    schoolLessonTopic: document.getElementById("schoolLessonTopic"),
    schoolLessonNotes: document.getElementById("schoolLessonNotes"),
    schoolLessonStatus: document.getElementById("schoolLessonStatus"),
    schoolLessonActive: document.getElementById("schoolLessonActive"),
    schoolLessonsBody: document.getElementById("schoolLessonsBody"),
    schoolStudentsBody: document.getElementById("schoolStudentsBody"),
    schoolAttendanceCourseId: document.getElementById("schoolAttendanceCourseId"),
    schoolAttendanceClassId: document.getElementById("schoolAttendanceClassId"),
    schoolAttendanceLessonId: document.getElementById("schoolAttendanceLessonId"),
    schoolAttendanceBody: document.getElementById("schoolAttendanceBody"),
    schoolAttendanceLoadBtn: document.getElementById("schoolAttendanceLoadBtn"),
    schoolAttendanceSaveBtn: document.getElementById("schoolAttendanceSaveBtn"),
    schoolCoursesAddBtn: document.getElementById("schoolCoursesAddBtn"),
    schoolClassesAddBtn: document.getElementById("schoolClassesAddBtn"),
    schoolProfessorsAddBtn: document.getElementById("schoolProfessorsAddBtn"),
    schoolLessonsAddBtn: document.getElementById("schoolLessonsAddBtn"),
    schoolStudentsAddBtn: document.getElementById("schoolStudentsAddBtn"),
    schoolCourseModal: document.getElementById("schoolCourseModal"),
    schoolCourseModalCloseBtn: document.getElementById("schoolCourseModalCloseBtn"),
    schoolCourseCancelBtn: document.getElementById("schoolCourseCancelBtn"),
    schoolCourseDeleteBtn: document.getElementById("schoolCourseDeleteBtn"),
    schoolCourseSaveBtn: document.getElementById("schoolCourseSaveBtn"),
    schoolCourseModalTitle: document.getElementById("schoolCourseModalTitle"),
    schoolClassModal: document.getElementById("schoolClassModal"),
    schoolClassModalCloseBtn: document.getElementById("schoolClassModalCloseBtn"),
    schoolClassCancelBtn: document.getElementById("schoolClassCancelBtn"),
    schoolClassDeleteBtn: document.getElementById("schoolClassDeleteBtn"),
    schoolClassSaveBtn: document.getElementById("schoolClassSaveBtn"),
    schoolClassModalTitle: document.getElementById("schoolClassModalTitle"),
    schoolProfessorModal: document.getElementById("schoolProfessorModal"),
    schoolProfessorModalCloseBtn: document.getElementById("schoolProfessorModalCloseBtn"),
    schoolProfessorCancelBtn: document.getElementById("schoolProfessorCancelBtn"),
    schoolProfessorDeleteBtn: document.getElementById("schoolProfessorDeleteBtn"),
    schoolProfessorSaveBtn: document.getElementById("schoolProfessorSaveBtn"),
    schoolProfessorModalTitle: document.getElementById("schoolProfessorModalTitle"),
    schoolLessonModal: document.getElementById("schoolLessonModal"),
    schoolLessonModalCloseBtn: document.getElementById("schoolLessonModalCloseBtn"),
    schoolLessonCancelBtn: document.getElementById("schoolLessonCancelBtn"),
    schoolLessonDeleteBtn: document.getElementById("schoolLessonDeleteBtn"),
    schoolLessonSaveBtn: document.getElementById("schoolLessonSaveBtn"),
    schoolLessonModalTitle: document.getElementById("schoolLessonModalTitle"),
    schoolStudentModal: document.getElementById("schoolStudentModal"),
    schoolStudentModalCloseBtn: document.getElementById("schoolStudentModalCloseBtn"),
    schoolStudentCancelBtn: document.getElementById("schoolStudentCancelBtn"),
    schoolStudentDeleteBtn: document.getElementById("schoolStudentDeleteBtn"),
    schoolStudentSaveBtn: document.getElementById("schoolStudentSaveBtn"),
    schoolStudentModalTitle: document.getElementById("schoolStudentModalTitle"),
    schoolStudentForm: document.getElementById("schoolStudentForm"),
    schoolStudentId: document.getElementById("schoolStudentId"),
    schoolStudentClassId: document.getElementById("schoolStudentClassId"),
    schoolStudentName: document.getElementById("schoolStudentName"),
    schoolStudentContact: document.getElementById("schoolStudentContact"),
    schoolStudentEmail: document.getElementById("schoolStudentEmail"),
    schoolStudentBirthDate: document.getElementById("schoolStudentBirthDate"),
    schoolStudentActive: document.getElementById("schoolStudentActive"),
    schoolDeleteModal: document.getElementById("schoolDeleteModal"),
    schoolDeleteModalText: document.getElementById("schoolDeleteModalText"),
    schoolDeleteModalCloseBtn: document.getElementById("schoolDeleteModalCloseBtn"),
    schoolDeleteCancelBtn: document.getElementById("schoolDeleteCancelBtn"),
    schoolDeleteConfirmBtn: document.getElementById("schoolDeleteConfirmBtn"),
  };

  if (!el.schoolBtn || !el.schoolModule) return;

  const state = {
    initialized: false,
    view: "courses",
    permissionSet: new Set(),
    isAdmin: false,
    courses: [],
    classes: [],
    professors: [],
    lessons: [],
    students: [],
    attendance: [],
    pendingDelete: null,
  };

  const weekdayLabel = {
    monday: "Segunda",
    tuesday: "Terca",
    wednesday: "Quarta",
    thursday: "Quinta",
    friday: "Sexta",
    saturday: "Sabado",
    sunday: "Domingo",
  };

  function valueOr(value, fallback) {
    return value == null ? fallback : value;
  }

  function getToken() {
    return valueOr(localStorage.getItem("accessToken"), "");
  }

  function setSchoolMessage(message, isError) {
    if (!el.schoolMessage) return;
    el.schoolMessage.textContent = message || "";
    el.schoolMessage.classList.toggle("error", Boolean(isError));
  }

  function setActiveModule(moduleName) {
    const isFinance = moduleName === "finance";
    const isCells = moduleName === "cells";
    const isSchool = moduleName === "school";

    if (el.financeBtn) el.financeBtn.classList.toggle("active", isFinance);
    if (el.cellsBtn) el.cellsBtn.classList.toggle("active", isCells);
    if (el.schoolBtn) el.schoolBtn.classList.toggle("active", isSchool);

    if (el.financeModule) el.financeModule.classList.toggle("hide", !isFinance);
    if (el.cellsModule) el.cellsModule.classList.toggle("hide", !isCells);
    if (el.schoolModule) el.schoolModule.classList.toggle("hide", !isSchool);
  }

  function setSchoolView(viewName) {
    const viewPermissions = {
      courses: "school_courses_view",
      classes: "school_classes_view",
      professors: "school_professors_view",
      lessons: "school_lessons_view",
      students: "school_students_view",
      attendance: "school_attendance_view",
      dashboard: "school_dashboard_view",
    };

    const requiredPermission = viewPermissions[viewName];
    if (requiredPermission && !hasPermission(requiredPermission)) {
      setSchoolMessage("Acesso negado: sua role nao permite esta tela.", true);
      const fallbackView = getFirstAllowedSchoolView();
      if (!fallbackView || fallbackView === viewName) {
        return;
      }
      viewName = fallbackView;
    }

    state.view = viewName;
    if (el.schoolNavCoursesBtn) el.schoolNavCoursesBtn.classList.toggle("active", viewName === "courses");
    if (el.schoolNavClassesBtn) el.schoolNavClassesBtn.classList.toggle("active", viewName === "classes");
    if (el.schoolNavProfessorsBtn) el.schoolNavProfessorsBtn.classList.toggle("active", viewName === "professors");
    if (el.schoolNavLessonsBtn) el.schoolNavLessonsBtn.classList.toggle("active", viewName === "lessons");
    if (el.schoolNavStudentsBtn) el.schoolNavStudentsBtn.classList.toggle("active", viewName === "students");
    if (el.schoolNavAttendanceBtn) el.schoolNavAttendanceBtn.classList.toggle("active", viewName === "attendance");
    if (el.schoolNavDashboardBtn) el.schoolNavDashboardBtn.classList.toggle("active", viewName === "dashboard");
    if (el.schoolCoursesView) el.schoolCoursesView.classList.toggle("hide", viewName !== "courses");
    if (el.schoolClassesView) el.schoolClassesView.classList.toggle("hide", viewName !== "classes");
    if (el.schoolProfessorsView) el.schoolProfessorsView.classList.toggle("hide", viewName !== "professors");
    if (el.schoolLessonsView) el.schoolLessonsView.classList.toggle("hide", viewName !== "lessons");
    if (el.schoolStudentsView) el.schoolStudentsView.classList.toggle("hide", viewName !== "students");
    if (el.schoolAttendanceView) el.schoolAttendanceView.classList.toggle("hide", viewName !== "attendance");
    if (el.schoolDashboardView) el.schoolDashboardView.classList.toggle("hide", viewName !== "dashboard");
  }

  function loadPermissionState() {
    try {
      const raw = localStorage.getItem(permissionStorageKey);
      const parsed = raw ? JSON.parse(raw) : [];
      const permissions = Array.isArray(parsed) ? parsed.filter(function (item) { return typeof item === "string"; }) : [];
      state.permissionSet = new Set(permissions);
    } catch (_error) {
      state.permissionSet = new Set();
    }
    state.isAdmin = localStorage.getItem(isAdminStorageKey) === "true";
  }

  function hasPermission(permissionName) {
    if (!permissionName) return false;
    if (state.isAdmin) return true;
    return state.permissionSet.has(permissionName);
  }

  function hasSchoolModuleAccess() {
    if (state.isAdmin) return true;
    for (const permissionName of state.permissionSet) {
      if (permissionName.indexOf("school_") === 0) return true;
    }
    return false;
  }

  function getFirstAllowedSchoolView() {
    const ordered = [
      ["dashboard", "school_dashboard_view"],
      ["courses", "school_courses_view"],
      ["classes", "school_classes_view"],
      ["professors", "school_professors_view"],
      ["lessons", "school_lessons_view"],
      ["students", "school_students_view"],
      ["attendance", "school_attendance_view"],
    ];

    for (const row of ordered) {
      if (hasPermission(row[1])) return row[0];
    }
    return null;
  }

  function applySchoolPermissionLayout() {
    const allowedByView = {
      courses: hasPermission("school_courses_view"),
      classes: hasPermission("school_classes_view"),
      professors: hasPermission("school_professors_view"),
      lessons: hasPermission("school_lessons_view"),
      students: hasPermission("school_students_view"),
      attendance: hasPermission("school_attendance_view"),
      dashboard: hasPermission("school_dashboard_view"),
    };

    if (el.schoolNavCoursesBtn) el.schoolNavCoursesBtn.classList.toggle("hide", !allowedByView.courses);
    if (el.schoolNavClassesBtn) el.schoolNavClassesBtn.classList.toggle("hide", !allowedByView.classes);
    if (el.schoolNavProfessorsBtn) el.schoolNavProfessorsBtn.classList.toggle("hide", !allowedByView.professors);
    if (el.schoolNavLessonsBtn) el.schoolNavLessonsBtn.classList.toggle("hide", !allowedByView.lessons);
    if (el.schoolNavStudentsBtn) el.schoolNavStudentsBtn.classList.toggle("hide", !allowedByView.students);
    if (el.schoolNavAttendanceBtn) el.schoolNavAttendanceBtn.classList.toggle("hide", !allowedByView.attendance);
    if (el.schoolNavDashboardBtn) el.schoolNavDashboardBtn.classList.toggle("hide", !allowedByView.dashboard);

    if (el.schoolBtn) {
      const canOpen = hasSchoolModuleAccess();
      el.schoolBtn.classList.toggle("hide", !canOpen);
      el.schoolBtn.disabled = !canOpen;
    }
  }

  async function api(path, options) {
    const token = getToken();
    if (!token) throw new Error("Sessao expirada. Faca login no Financeiro.");

    const response = await fetch(`${apiPrefix}${path}`, {
      method: options && options.method ? options.method : "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        ...(options && options.headers ? options.headers : {}),
      },
      body: options && options.body ? JSON.stringify(options.body) : undefined,
    });

    if (!response.ok) {
      let detail = "Falha na operacao.";
      try {
        const body = await response.json();
        if (body && typeof body.detail === "string") detail = body.detail;
      } catch (_error) {
      }
      if (detail.toLowerCase().includes("could not validate credentials")) {
        localStorage.removeItem("accessToken");
        throw new Error("Sessao expirada. Faca login novamente no Financeiro.");
      }
      throw new Error(detail);
    }

    if (response.status === 204) return null;
    return response.json();
  }

  function boolFromSelect(selectEl) {
    return valueOr(selectEl && selectEl.value, "true") === "true";
  }

  function resetCourseForm() {
    if (!el.schoolCourseForm) return;
    el.schoolCourseForm.reset();
    if (el.schoolCourseId) el.schoolCourseId.value = "";
    if (el.schoolCourseActive) el.schoolCourseActive.value = "true";
  }

  function resetClassForm() {
    if (!el.schoolClassForm) return;
    el.schoolClassForm.reset();
    if (el.schoolClassId) el.schoolClassId.value = "";
    if (el.schoolClassActive) el.schoolClassActive.value = "true";
  }

  function renderCourses() {
    if (!el.schoolCoursesBody) return;
    if (!state.courses.length) {
      el.schoolCoursesBody.innerHTML = '<tr><td colspan="4">Sem registros.</td></tr>';
      return;
    }

    el.schoolCoursesBody.innerHTML = state.courses
      .map(function (course) {
        const lessons = course.total_lessons == null ? "-" : String(course.total_lessons);
        const status = course.active ? "Ativo" : "Inativo";
        return `
          <tr>
            <td>${escapeHtml(course.name)}</td>
            <td>${lessons}</td>
            <td>${status}</td>
            <td>
              <button class="btn ghost btn-mini" data-course-edit="${course.id}" type="button">Editar</button>
              <button class="btn ghost btn-mini" data-course-delete="${course.id}" type="button">Excluir</button>
            </td>
          </tr>
        `;
      })
      .join("");
  }

  function renderClasses() {
    if (!el.schoolClassesBody) return;
    if (!state.classes.length) {
      el.schoolClassesBody.innerHTML = '<tr><td colspan="7">Sem registros.</td></tr>';
      return;
    }

    el.schoolClassesBody.innerHTML = state.classes
      .map(function (schoolClass) {
        const status = schoolClass.active ? "Ativa" : "Inativa";
        const weekday = valueOr(weekdayLabel[schoolClass.weekday], schoolClass.weekday);
        const schedule = `${valueOr(schoolClass.start_time, "--:--")} - ${valueOr(schoolClass.end_time, "--:--")}`;
        return `
          <tr>
            <td>${escapeHtml(schoolClass.name)}</td>
            <td>${escapeHtml(valueOr(schoolClass.course_name, "-"))}</td>
            <td>${escapeHtml(weekday)}</td>
            <td>${escapeHtml(schedule)}</td>
            <td>${escapeHtml(valueOr(schoolClass.professor_name, "-"))}</td>
            <td>${status}</td>
            <td>
              <button class="btn ghost btn-mini" data-class-edit="${schoolClass.id}" type="button">Editar</button>
              <button class="btn ghost btn-mini" data-class-delete="${schoolClass.id}" type="button">Excluir</button>
            </td>
          </tr>
        `;
      })
      .join("");
  }

  function renderCourseOptions() {
    if (!el.schoolClassCourseId) return;
    const options = ['<option value="">Selecione</option>'];
    state.courses.forEach(function (course) {
      options.push(`<option value="${course.id}">${escapeHtml(course.name)}</option>`);
    });
    const currentValue = el.schoolClassCourseId.value;
    el.schoolClassCourseId.innerHTML = options.join("");
    if (currentValue) el.schoolClassCourseId.value = currentValue;
  }

  function renderClassOptions() {
    if (!el.schoolLessonClassId) return;
    const options = ['<option value="">Selecione</option>'];
    state.classes.forEach(function (schoolClass) {
      const display = escapeHtml(schoolClass.class_name || schoolClass.name);
      options.push(`<option value="${schoolClass.id}">${display}</option>`);
    });
    const currentValue = el.schoolLessonClassId.value;
    el.schoolLessonClassId.innerHTML = options.join("");
    if (currentValue) el.schoolLessonClassId.value = currentValue;
  }

  function renderProfessorOptions() {
    if (!el.schoolLessonProfessorId) return;
    const options = ['<option value="">Selecione</option>'];
    state.professors.forEach(function (professor) {
      options.push(`<option value="${professor.id}">${escapeHtml(professor.name)}</option>`);
    });
    const currentValue = el.schoolLessonProfessorId.value;
    el.schoolLessonProfessorId.innerHTML = options.join("");
    if (currentValue) el.schoolLessonProfessorId.value = currentValue;
  }

  function renderStudentClassOptions() {
    if (!el.schoolStudentClassId) return;
    const options = ['<option value="">Selecione</option>'];
    state.classes.forEach(function (schoolClass) {
      options.push(`<option value="${schoolClass.id}">${escapeHtml(schoolClass.name)}</option>`);
    });
    const currentValue = el.schoolStudentClassId.value;
    el.schoolStudentClassId.innerHTML = options.join("");
    if (currentValue) el.schoolStudentClassId.value = currentValue;
  }

  function renderAttendanceCourseOptions() {
    if (!el.schoolAttendanceCourseId) return;
    const options = ['<option value="">Selecione</option>'];
    state.courses.forEach(function (course) {
      options.push(`<option value="${course.id}">${escapeHtml(course.name)}</option>`);
    });
    const currentValue = el.schoolAttendanceCourseId.value;
    el.schoolAttendanceCourseId.innerHTML = options.join("");
    if (currentValue) el.schoolAttendanceCourseId.value = currentValue;
  }

  function renderAttendanceClassOptions() {
    if (!el.schoolAttendanceClassId) return;
    const courseId = el.schoolAttendanceCourseId ? parseInt(el.schoolAttendanceCourseId.value) : null;
    const filteredClasses = courseId ? state.classes.filter(function (c) { return c.course_id === courseId; }) : [];
    
    const options = ['<option value="">Selecione</option>'];
    filteredClasses.forEach(function (cls) {
      const label = `${cls.name} (${valueOr(cls.weekday, "-")})`;
      options.push(`<option value="${cls.id}">${escapeHtml(label)}</option>`);
    });
    const currentValue = el.schoolAttendanceClassId.value;
    el.schoolAttendanceClassId.innerHTML = options.join("");
    if (currentValue) el.schoolAttendanceClassId.value = currentValue;
  }

  function renderLessonOptions() {
    if (!el.schoolAttendanceLessonId) return;
    const classId = el.schoolAttendanceClassId ? parseInt(el.schoolAttendanceClassId.value) : null;
    const filteredLessons = classId ? state.lessons.filter(function (l) { return l.class_id === classId; }) : [];
    
    const options = ['<option value="">Selecione</option>'];
    filteredLessons.forEach(function (lesson) {
      const topic = valueOr(lesson.topic, "");
      const label = `${valueOr(lesson.lesson_date, "-")}${topic ? " | " + topic : ""}`;
      options.push(`<option value="${lesson.id}">${escapeHtml(label)}</option>`);
    });
    const currentValue = el.schoolAttendanceLessonId.value;
    el.schoolAttendanceLessonId.innerHTML = options.join("");
    if (currentValue) el.schoolAttendanceLessonId.value = currentValue;
  }

  function renderStudents() {
    if (!el.schoolStudentsBody) return;
    if (!state.students.length) {
      el.schoolStudentsBody.innerHTML = '<tr><td colspan="6">Sem registros.</td></tr>';
      return;
    }

    el.schoolStudentsBody.innerHTML = state.students
      .map(function (student) {
        const status = student.active ? "Ativo" : "Inativo";
        return `
          <tr>
            <td>${escapeHtml(student.name)}</td>
            <td>${escapeHtml(valueOr(student.class_name, "-"))}</td>
            <td>${escapeHtml(valueOr(student.contact, "-"))}</td>
            <td>${escapeHtml(valueOr(student.email, "-"))}</td>
            <td>${status}</td>
            <td>
              <button class="btn ghost btn-mini" data-student-edit="${student.id}" type="button">Editar</button>
              <button class="btn ghost btn-mini" data-student-delete="${student.id}" type="button">Excluir</button>
            </td>
          </tr>
        `;
      })
      .join("");
  }

  function renderAttendance() {
    if (!el.schoolAttendanceBody) return;
    if (!state.attendance.length) {
      el.schoolAttendanceBody.innerHTML = '<tr><td colspan="3">Nenhum aluno encontrado para esta aula.</td></tr>';
      return;
    }

    el.schoolAttendanceBody.innerHTML = state.attendance
      .map(function (row) {
        return `
          <tr>
            <td>${escapeHtml(row.student_name)}</td>
            <td>
              <select data-attendance-status="${row.student_id}">
                <option value="pending" ${row.status === "pending" ? "selected" : ""}>Pendente</option>
                <option value="present" ${row.status === "present" ? "selected" : ""}>Presente</option>
                <option value="absent" ${row.status === "absent" ? "selected" : ""}>Falta</option>
                <option value="justified" ${row.status === "justified" ? "selected" : ""}>Falta justificada</option>
              </select>
            </td>
            <td>
              <input type="text" data-attendance-notes="${row.student_id}" value="${escapeHtml(valueOr(row.notes, ""))}" placeholder="Opcional">
            </td>
          </tr>
        `;
      })
      .join("");
  }

  function renderProfessors() {
    if (!el.schoolProfessorsBody) return;
    if (!state.professors.length) {
      el.schoolProfessorsBody.innerHTML = '<tr><td colspan="5">Sem registros.</td></tr>';
      return;
    }

    el.schoolProfessorsBody.innerHTML = state.professors
      .map(function (professor) {
        const status = professor.active ? "Ativo" : "Inativo";
        return `
          <tr>
            <td>${escapeHtml(professor.name)}</td>
            <td>${escapeHtml(valueOr(professor.contact, "-"))}</td>
            <td>${escapeHtml(valueOr(professor.email, "-"))}</td>
            <td>${status}</td>
            <td>
              <button class="btn ghost btn-mini" data-professor-edit="${professor.id}" type="button">Editar</button>
              <button class="btn ghost btn-mini" data-professor-delete="${professor.id}" type="button">Excluir</button>
            </td>
          </tr>
        `;
      })
      .join("");
  }

  function renderLessons() {
    if (!el.schoolLessonsBody) return;
    if (!state.lessons.length) {
      el.schoolLessonsBody.innerHTML = '<tr><td colspan="6">Sem registros.</td></tr>';
      return;
    }

    el.schoolLessonsBody.innerHTML = state.lessons
      .map(function (lesson) {
        const statusMap = { scheduled: "Agendada", completed: "Realizada", cancelled: "Cancelada" };
        const status = valueOr(statusMap[lesson.status], lesson.status);
        return `
          <tr>
            <td>${escapeHtml(valueOr(lesson.lesson_date, "-"))}</td>
            <td>${escapeHtml(valueOr(lesson.class_name, "-"))}</td>
            <td>${escapeHtml(valueOr(lesson.professor_name, "-"))}</td>
            <td>${escapeHtml(valueOr(lesson.topic, "-"))}</td>
            <td>${status}</td>
            <td>
              <button class="btn ghost btn-mini" data-lesson-edit="${lesson.id}" type="button">Editar</button>
              <button class="btn ghost btn-mini" data-lesson-delete="${lesson.id}" type="button">Excluir</button>
            </td>
          </tr>
        `;
      })
      .join("");
  }

  function resetProfessorForm() {
    if (!el.schoolProfessorForm) return;
    el.schoolProfessorForm.reset();
    if (el.schoolProfessorId) el.schoolProfessorId.value = "";
    if (el.schoolProfessorActive) el.schoolProfessorActive.value = "true";
  }

  function resetLessonForm() {
    if (!el.schoolLessonForm) return;
    el.schoolLessonForm.reset();
    if (el.schoolLessonId) el.schoolLessonId.value = "";
    if (el.schoolLessonDate) el.schoolLessonDate.value = "";
    if (el.schoolLessonStatus) el.schoolLessonStatus.value = "scheduled";
    if (el.schoolLessonActive) el.schoolLessonActive.value = "true";
  }

  function resetStudentForm() {
    if (!el.schoolStudentForm) return;
    el.schoolStudentForm.reset();
    if (el.schoolStudentId) el.schoolStudentId.value = "";
    if (el.schoolStudentActive) el.schoolStudentActive.value = "true";
  }

  function editProfessorById(professorId) {
    const professor = state.professors.find(function (row) {
      return row.id === professorId;
    });
    if (!professor) return;

    if (el.schoolProfessorId) el.schoolProfessorId.value = String(professor.id);
    if (el.schoolProfessorName) el.schoolProfessorName.value = valueOr(professor.name, "");
    if (el.schoolProfessorContact) el.schoolProfessorContact.value = valueOr(professor.contact, "");
    if (el.schoolProfessorEmail) el.schoolProfessorEmail.value = valueOr(professor.email, "");
    if (el.schoolProfessorBio) el.schoolProfessorBio.value = valueOr(professor.bio, "");
    if (el.schoolProfessorActive) el.schoolProfessorActive.value = professor.active ? "true" : "false";
    setSchoolView("professors");
  }

  function editLessonById(lessonId) {
    const lesson = state.lessons.find(function (row) {
      return row.id === lessonId;
    });
    if (!lesson) return;

    if (el.schoolLessonId) el.schoolLessonId.value = String(lesson.id);
    if (el.schoolLessonClassId) el.schoolLessonClassId.value = String(lesson.class_id);
    if (el.schoolLessonProfessorId) el.schoolLessonProfessorId.value = String(lesson.professor_id || "");
    if (el.schoolLessonDate) el.schoolLessonDate.value = valueOr(lesson.lesson_date, "");
    if (el.schoolLessonTopic) el.schoolLessonTopic.value = valueOr(lesson.topic, "");
    if (el.schoolLessonNotes) el.schoolLessonNotes.value = valueOr(lesson.notes, "");
    if (el.schoolLessonStatus) el.schoolLessonStatus.value = valueOr(lesson.status, "scheduled");
    if (el.schoolLessonActive) el.schoolLessonActive.value = lesson.active ? "true" : "false";
    setSchoolView("lessons");
  }

  function editStudentById(studentId) {
    const student = state.students.find(function (row) {
      return row.id === studentId;
    });
    if (!student) return;

    if (el.schoolStudentId) el.schoolStudentId.value = String(student.id);
    if (el.schoolStudentClassId) el.schoolStudentClassId.value = String(student.class_id);
    if (el.schoolStudentName) el.schoolStudentName.value = valueOr(student.name, "");
    if (el.schoolStudentContact) el.schoolStudentContact.value = valueOr(student.contact, "");
    if (el.schoolStudentEmail) el.schoolStudentEmail.value = valueOr(student.email, "");
    if (el.schoolStudentBirthDate) el.schoolStudentBirthDate.value = valueOr(student.birth_date, "");
    if (el.schoolStudentActive) el.schoolStudentActive.value = student.active ? "true" : "false";
    setSchoolView("students");
  }

  async function loadProfessors() {
    state.professors = await api("/bible-school/professors");
    renderProfessors();
    renderProfessorOptions();
  }

  async function loadLessons() {
    state.lessons = await api("/bible-school/lessons");
    renderLessons();
    renderLessonOptions();
  }

  async function loadStudents() {
    state.students = await api("/bible-school/students");
    renderStudents();
  }

  async function loadAttendanceByLesson(lessonId) {
    if (!lessonId) {
      state.attendance = [];
      renderAttendance();
      return;
    }
    state.attendance = await api(`/bible-school/lessons/${lessonId}/attendance`);
    renderAttendance();
  }

  async function loadCourses() {
    state.courses = await api("/bible-school/courses");
    renderCourses();
    renderCourseOptions();
  }

  async function refreshAll() {
    if (hasPermission("school_courses_view")) {
      await loadCourses();
    } else {
      state.courses = [];
      renderCourses();
    }

    if (hasPermission("school_classes_view")) {
      await loadClasses();
    } else {
      state.classes = [];
      renderClasses();
    }

    if (hasPermission("school_professors_view")) {
      await loadProfessors();
    } else {
      state.professors = [];
      renderProfessors();
    }

    if (hasPermission("school_lessons_view")) {
      await loadLessons();
    } else {
      state.lessons = [];
      renderLessons();
    }

    if (hasPermission("school_students_view")) {
      await loadStudents();
    } else {
      state.students = [];
      renderStudents();
    }
  }

  // Modal management functions
  function openCourseModal(courseId = null) {
    if (courseId) {
      const course = state.courses.find(function (row) {
        return row.id === courseId;
      });
      if (!course) return;
      if (el.schoolCourseId) el.schoolCourseId.value = String(course.id);
      if (el.schoolCourseName) el.schoolCourseName.value = valueOr(course.name, "");
      if (el.schoolCourseDescription) el.schoolCourseDescription.value = valueOr(course.description, "");
      if (el.schoolCourseTotalLessons) el.schoolCourseTotalLessons.value = course.total_lessons == null ? "" : String(course.total_lessons);
      if (el.schoolCourseActive) el.schoolCourseActive.value = course.active ? "true" : "false";
      if (el.schoolCourseModalTitle) el.schoolCourseModalTitle.textContent = "Editar curso";
      if (el.schoolCourseDeleteBtn) el.schoolCourseDeleteBtn.classList.remove("hide");
    } else {
      if (el.schoolCourseForm) el.schoolCourseForm.reset();
      if (el.schoolCourseId) el.schoolCourseId.value = "";
      if (el.schoolCourseActive) el.schoolCourseActive.value = "true";
      if (el.schoolCourseModalTitle) el.schoolCourseModalTitle.textContent = "Cadastrar curso";
      if (el.schoolCourseDeleteBtn) el.schoolCourseDeleteBtn.classList.add("hide");
    }
    if (el.schoolCourseModal) el.schoolCourseModal.classList.remove("hide");
  }

  function closeCourseModal() {
    if (el.schoolCourseModal) el.schoolCourseModal.classList.add("hide");
  }

  function openClassModal(classId = null) {
    if (classId) {
      const schoolClass = state.classes.find(function (row) {
        return row.id === classId;
      });
      if (!schoolClass) return;
      if (el.schoolClassId) el.schoolClassId.value = String(schoolClass.id);
      if (el.schoolClassCourseId) el.schoolClassCourseId.value = String(schoolClass.course_id);
      if (el.schoolClassName) el.schoolClassName.value = valueOr(schoolClass.name, "");
      if (el.schoolClassWeekday) el.schoolClassWeekday.value = valueOr(schoolClass.weekday, "monday");
      if (el.schoolClassStartTime) el.schoolClassStartTime.value = valueOr(schoolClass.start_time, "");
      if (el.schoolClassEndTime) el.schoolClassEndTime.value = valueOr(schoolClass.end_time, "");
      if (el.schoolClassProfessorName) el.schoolClassProfessorName.value = valueOr(schoolClass.professor_name, "");
      if (el.schoolClassContact) el.schoolClassContact.value = valueOr(schoolClass.contact, "");
      if (el.schoolClassActive) el.schoolClassActive.value = schoolClass.active ? "true" : "false";
      if (el.schoolClassModalTitle) el.schoolClassModalTitle.textContent = "Editar turma";
      if (el.schoolClassDeleteBtn) el.schoolClassDeleteBtn.classList.remove("hide");
    } else {
      if (el.schoolClassForm) el.schoolClassForm.reset();
      if (el.schoolClassId) el.schoolClassId.value = "";
      if (el.schoolClassActive) el.schoolClassActive.value = "true";
      if (el.schoolClassModalTitle) el.schoolClassModalTitle.textContent = "Cadastrar turma";
      if (el.schoolClassDeleteBtn) el.schoolClassDeleteBtn.classList.add("hide");
    }
    if (el.schoolClassModal) el.schoolClassModal.classList.remove("hide");
  }

  function closeClassModal() {
    if (el.schoolClassModal) el.schoolClassModal.classList.add("hide");
  }

  function openProfessorModal(professorId = null) {
    if (professorId) {
      const professor = state.professors.find(function (row) {
        return row.id === professorId;
      });
      if (!professor) return;
      if (el.schoolProfessorId) el.schoolProfessorId.value = String(professor.id);
      if (el.schoolProfessorName) el.schoolProfessorName.value = valueOr(professor.name, "");
      if (el.schoolProfessorContact) el.schoolProfessorContact.value = valueOr(professor.contact, "");
      if (el.schoolProfessorEmail) el.schoolProfessorEmail.value = valueOr(professor.email, "");
      if (el.schoolProfessorBio) el.schoolProfessorBio.value = valueOr(professor.bio, "");
      if (el.schoolProfessorActive) el.schoolProfessorActive.value = professor.active ? "true" : "false";
      if (el.schoolProfessorModalTitle) el.schoolProfessorModalTitle.textContent = "Editar professor";
      if (el.schoolProfessorDeleteBtn) el.schoolProfessorDeleteBtn.classList.remove("hide");
    } else {
      if (el.schoolProfessorForm) el.schoolProfessorForm.reset();
      if (el.schoolProfessorId) el.schoolProfessorId.value = "";
      if (el.schoolProfessorActive) el.schoolProfessorActive.value = "true";
      if (el.schoolProfessorModalTitle) el.schoolProfessorModalTitle.textContent = "Cadastrar professor";
      if (el.schoolProfessorDeleteBtn) el.schoolProfessorDeleteBtn.classList.add("hide");
    }
    if (el.schoolProfessorModal) el.schoolProfessorModal.classList.remove("hide");
  }

  function closeProfessorModal() {
    if (el.schoolProfessorModal) el.schoolProfessorModal.classList.add("hide");
  }

  function openLessonModal(lessonId = null) {
    if (lessonId) {
      const lesson = state.lessons.find(function (row) {
        return row.id === lessonId;
      });
      if (!lesson) return;
      if (el.schoolLessonId) el.schoolLessonId.value = String(lesson.id);
      if (el.schoolLessonClassId) el.schoolLessonClassId.value = String(lesson.class_id);
      if (el.schoolLessonProfessorId) el.schoolLessonProfessorId.value = String(lesson.professor_id || "");
      if (el.schoolLessonDate) el.schoolLessonDate.value = valueOr(lesson.lesson_date, "");
      if (el.schoolLessonTopic) el.schoolLessonTopic.value = valueOr(lesson.topic, "");
      if (el.schoolLessonNotes) el.schoolLessonNotes.value = valueOr(lesson.notes, "");
      if (el.schoolLessonStatus) el.schoolLessonStatus.value = valueOr(lesson.status, "scheduled");
      if (el.schoolLessonActive) el.schoolLessonActive.value = lesson.active ? "true" : "false";
      if (el.schoolLessonModalTitle) el.schoolLessonModalTitle.textContent = "Editar aula";
      if (el.schoolLessonDeleteBtn) el.schoolLessonDeleteBtn.classList.remove("hide");
    } else {
      if (el.schoolLessonForm) el.schoolLessonForm.reset();
      if (el.schoolLessonId) el.schoolLessonId.value = "";
      if (el.schoolLessonDate) el.schoolLessonDate.value = "";
      if (el.schoolLessonStatus) el.schoolLessonStatus.value = "scheduled";
      if (el.schoolLessonActive) el.schoolLessonActive.value = "true";
      if (el.schoolLessonModalTitle) el.schoolLessonModalTitle.textContent = "Cadastrar aula";
      if (el.schoolLessonDeleteBtn) el.schoolLessonDeleteBtn.classList.add("hide");
    }
    if (el.schoolLessonModal) el.schoolLessonModal.classList.remove("hide");
  }

  function closeLessonModal() {
    if (el.schoolLessonModal) el.schoolLessonModal.classList.add("hide");
  }

  function openStudentModal(studentId = null) {
    if (studentId) {
      const student = state.students.find(function (row) {
        return row.id === studentId;
      });
      if (!student) return;
      if (el.schoolStudentId) el.schoolStudentId.value = String(student.id);
      if (el.schoolStudentClassId) el.schoolStudentClassId.value = String(student.class_id);
      if (el.schoolStudentName) el.schoolStudentName.value = valueOr(student.name, "");
      if (el.schoolStudentContact) el.schoolStudentContact.value = valueOr(student.contact, "");
      if (el.schoolStudentEmail) el.schoolStudentEmail.value = valueOr(student.email, "");
      if (el.schoolStudentBirthDate) el.schoolStudentBirthDate.value = valueOr(student.birth_date, "");
      if (el.schoolStudentActive) el.schoolStudentActive.value = student.active ? "true" : "false";
      if (el.schoolStudentModalTitle) el.schoolStudentModalTitle.textContent = "Editar aluno";
      if (el.schoolStudentDeleteBtn) el.schoolStudentDeleteBtn.classList.remove("hide");
    } else {
      resetStudentForm();
      if (el.schoolStudentModalTitle) el.schoolStudentModalTitle.textContent = "Cadastrar aluno";
      if (el.schoolStudentDeleteBtn) el.schoolStudentDeleteBtn.classList.add("hide");
    }
    if (el.schoolStudentModal) el.schoolStudentModal.classList.remove("hide");
  }

  function closeStudentModal() {
    if (el.schoolStudentModal) el.schoolStudentModal.classList.add("hide");
  }

  function openDeleteModal(entityType, entityId) {
    const labels = {
      course: "este curso",
      class: "esta turma",
      professor: "este professor",
      lesson: "esta aula",
      student: "este aluno",
    };
    state.pendingDelete = { type: entityType, id: entityId };
    if (el.schoolDeleteModalText) {
      const label = valueOr(labels[entityType], "este registro");
      el.schoolDeleteModalText.textContent = `Tem certeza que deseja excluir ${label}?`;
    }
    if (el.schoolDeleteModal) el.schoolDeleteModal.classList.remove("hide");
  }

  function closeDeleteModal() {
    if (el.schoolDeleteModal) el.schoolDeleteModal.classList.add("hide");
    state.pendingDelete = null;
  }

  function closeAllSchoolModals() {
    closeCourseModal();
    closeClassModal();
    closeProfessorModal();
    closeLessonModal();
    closeStudentModal();
    closeDeleteModal();
  }

  function isSchoolModalOverlay(target) {
    return (
      target === el.schoolCourseModal ||
      target === el.schoolClassModal ||
      target === el.schoolProfessorModal ||
      target === el.schoolLessonModal ||
      target === el.schoolStudentModal ||
      target === el.schoolDeleteModal
    );
  }

  async function confirmDeleteModal() {
    if (!state.pendingDelete) return;
    const pending = state.pendingDelete;
    closeDeleteModal();

    if (pending.type === "course") {
      await deleteCourse(pending.id);
      return;
    }
    if (pending.type === "class") {
      await deleteClass(pending.id);
      return;
    }
    if (pending.type === "professor") {
      await deleteProfessor(pending.id);
      return;
    }
    if (pending.type === "lesson") {
      await deleteLesson(pending.id);
      return;
    }
    if (pending.type === "student") {
      await deleteStudent(pending.id);
    }
  }

  async function submitProfessorForm(event) {
    event.preventDefault();
    setSchoolMessage("", false);

    const id = Number(valueOr(el.schoolProfessorId && el.schoolProfessorId.value, ""));
    const payload = {
      name: valueOr(el.schoolProfessorName && el.schoolProfessorName.value, "").trim(),
      contact: valueOr(el.schoolProfessorContact && el.schoolProfessorContact.value, "").trim() || null,
      email: valueOr(el.schoolProfessorEmail && el.schoolProfessorEmail.value, "").trim() || null,
      bio: valueOr(el.schoolProfessorBio && el.schoolProfessorBio.value, "").trim() || null,
      active: boolFromSelect(el.schoolProfessorActive),
    };

    if (!payload.name) {
      setSchoolMessage("Informe o nome do professor.", true);
      return;
    }

    if (id) {
      await api(`/bible-school/professors/${id}`, { method: "PUT", body: payload });
      setSchoolMessage("Professor atualizado com sucesso.", false);
    } else {
      await api("/bible-school/professors", { method: "POST", body: payload });
      setSchoolMessage("Professor cadastrado com sucesso.", false);
    }

    closeProfessorModal();
    await loadProfessors();
  }

  async function deleteProfessor(professorId) {
    setSchoolMessage("", false);
    await api(`/bible-school/professors/${professorId}`, { method: "DELETE" });
    setSchoolMessage("Professor excluído com sucesso.", false);
    closeProfessorModal();
    await loadProfessors();
  }

  async function submitLessonForm(event) {
    event.preventDefault();
    setSchoolMessage("", false);

    const id = Number(valueOr(el.schoolLessonId && el.schoolLessonId.value, ""));
    const classId = Number(valueOr(el.schoolLessonClassId && el.schoolLessonClassId.value, ""));
    const professorId = valueOr(el.schoolLessonProfessorId && el.schoolLessonProfessorId.value, "");
    const payload = {
      class_id: classId,
      professor_id: professorId ? Number(professorId) : null,
      lesson_date: valueOr(el.schoolLessonDate && el.schoolLessonDate.value, ""),
      topic: valueOr(el.schoolLessonTopic && el.schoolLessonTopic.value, "").trim() || null,
      notes: valueOr(el.schoolLessonNotes && el.schoolLessonNotes.value, "").trim() || null,
      status: valueOr(el.schoolLessonStatus && el.schoolLessonStatus.value, "scheduled"),
      active: boolFromSelect(el.schoolLessonActive),
    };

    if (!classId || !payload.lesson_date) {
      setSchoolMessage("Preencha turma e data da aula.", true);
      return;
    }

    if (id) {
      await api(`/bible-school/lessons/${id}`, { method: "PUT", body: payload });
      setSchoolMessage("Aula atualizada com sucesso.", false);
    } else {
      await api("/bible-school/lessons", { method: "POST", body: payload });
      setSchoolMessage("Aula cadastrada com sucesso.", false);
    }

    closeLessonModal();
    await loadLessons();
  }

  async function deleteLesson(lessonId) {
    setSchoolMessage("", false);
    await api(`/bible-school/lessons/${lessonId}`, { method: "DELETE" });
    setSchoolMessage("Aula excluída com sucesso.", false);
    closeLessonModal();
    await loadLessons();
  }

  async function submitStudentForm(event) {
    event.preventDefault();
    setSchoolMessage("", false);

    const id = Number(valueOr(el.schoolStudentId && el.schoolStudentId.value, ""));
    const payload = {
      class_id: Number(valueOr(el.schoolStudentClassId && el.schoolStudentClassId.value, "")),
      name: valueOr(el.schoolStudentName && el.schoolStudentName.value, "").trim(),
      contact: valueOr(el.schoolStudentContact && el.schoolStudentContact.value, "").trim() || null,
      email: valueOr(el.schoolStudentEmail && el.schoolStudentEmail.value, "").trim() || null,
      birth_date: valueOr(el.schoolStudentBirthDate && el.schoolStudentBirthDate.value, "") || null,
      active: boolFromSelect(el.schoolStudentActive),
    };

    if (!payload.class_id || !payload.name) {
      setSchoolMessage("Preencha turma e nome do aluno.", true);
      return;
    }

    if (id) {
      await api(`/bible-school/students/${id}`, { method: "PUT", body: payload });
      setSchoolMessage("Aluno atualizado com sucesso.", false);
    } else {
      await api("/bible-school/students", { method: "POST", body: payload });
      setSchoolMessage("Aluno cadastrado com sucesso.", false);
    }

    closeStudentModal();
    await loadStudents();
  }

  async function deleteStudent(studentId) {
    setSchoolMessage("", false);
    await api(`/bible-school/students/${studentId}`, { method: "DELETE" });
    setSchoolMessage("Aluno excluído com sucesso.", false);
    closeStudentModal();
    await loadStudents();
  }

  async function saveAttendance() {
    const lessonId = Number(valueOr(el.schoolAttendanceLessonId && el.schoolAttendanceLessonId.value, ""));
    if (!lessonId) {
      setSchoolMessage("Selecione uma aula para salvar a chamada.", true);
      return;
    }

    const items = state.attendance.map(function (row) {
      const statusEl = el.schoolAttendanceBody && el.schoolAttendanceBody.querySelector(`[data-attendance-status="${row.student_id}"]`);
      const notesEl = el.schoolAttendanceBody && el.schoolAttendanceBody.querySelector(`[data-attendance-notes="${row.student_id}"]`);
      return {
        student_id: row.student_id,
        status: valueOr(statusEl && statusEl.value, "pending"),
        notes: valueOr(notesEl && notesEl.value, "").trim() || null,
      };
    });

    await api(`/bible-school/lessons/${lessonId}/attendance`, {
      method: "PUT",
      body: { items: items },
    });
    setSchoolMessage("Chamada salva com sucesso.", false);
    await loadAttendanceByLesson(lessonId);
  }

  async function loadDashboardData() {
    // Renders the filters and initializes the dashboard
    renderDashboardCourseOptions();
    renderDashboardClassOptions();
    renderDashboardStats();
  }

  function renderDashboardCourseOptions() {
    if (!el.schoolDashboardCourseId) return;
    const options = ['<option value="">Todos</option>'];
    state.courses.forEach(function (course) {
      options.push(`<option value="${course.id}">${escapeHtml(course.name)}</option>`);
    });
    const currentValue = el.schoolDashboardCourseId.value;
    el.schoolDashboardCourseId.innerHTML = options.join("");
    if (currentValue) el.schoolDashboardCourseId.value = currentValue;
  }

  function renderDashboardClassOptions() {
    if (!el.schoolDashboardClassId) return;
    const courseId = el.schoolDashboardCourseId ? parseInt(el.schoolDashboardCourseId.value) : null;
    const filteredClasses = courseId ? state.classes.filter(function (c) { return c.course_id === courseId; }) : state.classes;
    
    const options = ['<option value="">Todas</option>'];
    filteredClasses.forEach(function (cls) {
      options.push(`<option value="${cls.id}">${escapeHtml(cls.name)}</option>`);
    });
    const currentValue = el.schoolDashboardClassId.value;
    el.schoolDashboardClassId.innerHTML = options.join("");
    if (currentValue) el.schoolDashboardClassId.value = currentValue;
  }

  function calculateDashboardStats() {
    const courseId = el.schoolDashboardCourseId ? parseInt(el.schoolDashboardCourseId.value) : null;
    const classId = el.schoolDashboardClassId ? parseInt(el.schoolDashboardClassId.value) : null;
    const minPercentage = parseInt(el.schoolDashboardMinPercentage ? el.schoolDashboardMinPercentage.value : 70);

    // Filter classes
    const filteredClasses = state.classes.filter(function (c) {
      if (courseId && c.course_id !== courseId) return false;
      if (classId && c.id !== classId) return false;
      return true;
    });
    const classIds = filteredClasses.map(function (c) { return c.id; });

    // Filter lessons
    const filteredLessons = classIds.length > 0 
      ? state.lessons.filter(function (l) { return classIds.indexOf(l.class_id) !== -1; })
      : [];
    const lessonIds = filteredLessons.map(function (l) { return l.id; });
    const totalLessons = lessonIds.length;

    // Filter students
    const filteredStudents = classIds.length > 0
      ? state.students.filter(function (s) { return classIds.indexOf(s.class_id) !== -1; })
      : [];
    const totalStudents = filteredStudents.length;

    // Calculate attendance stats per student
    const studentStats = [];
    filteredStudents.forEach(function (student) {
      const studentAttendance = state.attendance.filter(function (a) { return a.student_id === student.id && lessonIds.indexOf(a.lesson_id) !== -1; });
      const presentCount = studentAttendance.filter(function (a) { return a.status === "present"; }).length;
      const percentage = totalLessons > 0 ? Math.round((presentCount / totalLessons) * 100) : 0;
      const approved = totalLessons > 0 ? percentage >= minPercentage : false;
      
      studentStats.push({
        student_id: student.id,
        name: student.name,
        present: presentCount,
        total: totalLessons,
        percentage: percentage,
        approved: approved
      });
    });

    // Calculate aggregate stats
    const approvedCount = studentStats.filter(function (s) { return s.approved; }).length;
    const failedCount = studentStats.filter(function (s) { return !s.approved; }).length;
    const avgAttendance = studentStats.length > 0 
      ? Math.round(studentStats.reduce(function (sum, s) { return sum + s.percentage; }, 0) / studentStats.length)
      : 0;
    const approvalRate = totalStudents > 0 ? Math.round((approvedCount / totalStudents) * 100) : 0;

    return {
      totalLessons: totalLessons,
      totalStudents: totalStudents,
      avgAttendance: avgAttendance,
      approvedCount: approvedCount,
      failedCount: failedCount,
      approvalRate: approvalRate,
      studentStats: studentStats
    };
  }

  function renderDashboardStats() {
    const stats = calculateDashboardStats();

    // Update stat cards
    if (el.dashboardTotalLessons) el.dashboardTotalLessons.textContent = stats.totalLessons;
    if (el.dashboardTotalStudents) el.dashboardTotalStudents.textContent = stats.totalStudents;
    if (el.dashboardAvgAttendance) el.dashboardAvgAttendance.textContent = stats.avgAttendance + "%";
    if (el.dashboardApprovedCount) el.dashboardApprovedCount.textContent = stats.approvedCount;
    if (el.dashboardFailedCount) el.dashboardFailedCount.textContent = stats.failedCount;
    if (el.dashboardApprovalRate) el.dashboardApprovalRate.textContent = stats.approvalRate + "%";

    // Render student table
    if (!el.schoolDashboardBody) return;
    if (stats.studentStats.length === 0) {
      el.schoolDashboardBody.innerHTML = '<tr><td colspan="5">Sem dados para os filtros selecionados.</td></tr>';
      return;
    }

    el.schoolDashboardBody.innerHTML = stats.studentStats
      .map(function (student) {
        const statusBadge = student.approved 
          ? '<span style="color: #27ae60; font-weight: 600;">✓ Aprovado</span>'
          : '<span style="color: #e74c3c; font-weight: 600;">✗ Reprovado</span>';
        return `<tr>
          <td>${escapeHtml(student.name)}</td>
          <td>${student.present}</td>
          <td>${student.total}</td>
          <td>${student.percentage}%</td>
          <td>${statusBadge}</td>
        </tr>`;
      })
      .join("");
  }

  function escapeHtml(text) {
    return String(valueOr(text, ""))
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  async function loadClasses() {
    state.classes = await api("/bible-school/classes");
    renderClasses();
    renderClassOptions();
    renderStudentClassOptions();
  }

  function editCourseById(courseId) {
    const course = state.courses.find(function (row) {
      return row.id === courseId;
    });
    if (!course) return;

    if (el.schoolCourseId) el.schoolCourseId.value = String(course.id);
    if (el.schoolCourseName) el.schoolCourseName.value = valueOr(course.name, "");
    if (el.schoolCourseDescription) el.schoolCourseDescription.value = valueOr(course.description, "");
    if (el.schoolCourseTotalLessons) {
      el.schoolCourseTotalLessons.value = course.total_lessons == null ? "" : String(course.total_lessons);
    }
    if (el.schoolCourseActive) el.schoolCourseActive.value = course.active ? "true" : "false";
    setSchoolView("courses");
  }

  function editClassById(classId) {
    const schoolClass = state.classes.find(function (row) {
      return row.id === classId;
    });
    if (!schoolClass) return;

    if (el.schoolClassId) el.schoolClassId.value = String(schoolClass.id);
    if (el.schoolClassCourseId) el.schoolClassCourseId.value = String(schoolClass.course_id);
    if (el.schoolClassName) el.schoolClassName.value = valueOr(schoolClass.name, "");
    if (el.schoolClassWeekday) el.schoolClassWeekday.value = valueOr(schoolClass.weekday, "monday");
    if (el.schoolClassStartTime) el.schoolClassStartTime.value = valueOr(schoolClass.start_time, "");
    if (el.schoolClassEndTime) el.schoolClassEndTime.value = valueOr(schoolClass.end_time, "");
    if (el.schoolClassProfessorName) el.schoolClassProfessorName.value = valueOr(schoolClass.professor_name, "");
    if (el.schoolClassContact) el.schoolClassContact.value = valueOr(schoolClass.contact, "");
    if (el.schoolClassActive) el.schoolClassActive.value = schoolClass.active ? "true" : "false";
    setSchoolView("classes");
  }

  async function submitCourseForm(event) {
    event.preventDefault();
    setSchoolMessage("", false);

    const id = Number(valueOr(el.schoolCourseId && el.schoolCourseId.value, ""));
    const payload = {
      name: valueOr(el.schoolCourseName && el.schoolCourseName.value, "").trim(),
      description: valueOr(el.schoolCourseDescription && el.schoolCourseDescription.value, "").trim() || null,
      total_lessons: valueOr(el.schoolCourseTotalLessons && el.schoolCourseTotalLessons.value, "")
        ? Number(el.schoolCourseTotalLessons.value)
        : null,
      active: boolFromSelect(el.schoolCourseActive),
    };

    if (!payload.name) {
      setSchoolMessage("Informe o nome do curso.", true);
      return;
    }

    if (id) {
      await api(`/bible-school/courses/${id}`, { method: "PUT", body: payload });
      setSchoolMessage("Curso atualizado com sucesso.", false);
    } else {
      await api("/bible-school/courses", { method: "POST", body: payload });
      setSchoolMessage("Curso cadastrado com sucesso.", false);
    }

    closeCourseModal();
    await refreshAll();
  }

  async function deleteCourse(courseId) {
    setSchoolMessage("", false);
    await api(`/bible-school/courses/${courseId}`, { method: "DELETE" });
    setSchoolMessage("Curso excluído com sucesso.", false);
    closeCourseModal();
    await refreshAll();
  }

  async function submitClassForm(event) {
    event.preventDefault();
    setSchoolMessage("", false);

    const id = Number(valueOr(el.schoolClassId && el.schoolClassId.value, ""));
    const payload = {
      course_id: Number(valueOr(el.schoolClassCourseId && el.schoolClassCourseId.value, "")),
      name: valueOr(el.schoolClassName && el.schoolClassName.value, "").trim(),
      weekday: valueOr(el.schoolClassWeekday && el.schoolClassWeekday.value, "monday"),
      start_time: valueOr(el.schoolClassStartTime && el.schoolClassStartTime.value, ""),
      end_time: valueOr(el.schoolClassEndTime && el.schoolClassEndTime.value, ""),
      professor_name: valueOr(el.schoolClassProfessorName && el.schoolClassProfessorName.value, "").trim() || null,
      contact: valueOr(el.schoolClassContact && el.schoolClassContact.value, "").trim() || null,
      active: boolFromSelect(el.schoolClassActive),
    };

    if (!payload.course_id || !payload.name || !payload.start_time || !payload.end_time) {
      setSchoolMessage("Preencha os campos obrigatorios da turma.", true);
      return;
    }

    if (id) {
      await api(`/bible-school/classes/${id}`, { method: "PUT", body: payload });
      setSchoolMessage("Turma atualizada com sucesso.", false);
    } else {
      await api("/bible-school/classes", { method: "POST", body: payload });
      setSchoolMessage("Turma cadastrada com sucesso.", false);
    }

    closeClassModal();
    await refreshAll();
  }

  async function deleteClass(classId) {
    setSchoolMessage("", false);
    await api(`/bible-school/classes/${classId}`, { method: "DELETE" });
    setSchoolMessage("Turma excluída com sucesso.", false);
    closeClassModal();
    await refreshAll();
  }

  async function ensureSchoolInitialized() {
    if (state.initialized) return;
    loadPermissionState();
    applySchoolPermissionLayout();
    await refreshAll();
    resetCourseForm();
    resetClassForm();
    resetProfessorForm();
    resetLessonForm();
    resetStudentForm();
    state.initialized = true;
  }

  async function openSchoolModule() {
    loadPermissionState();
    applySchoolPermissionLayout();
    if (!hasSchoolModuleAccess()) {
      throw new Error("Acesso negado ao modulo Escola Biblica.");
    }

    const fallbackView = getFirstAllowedSchoolView();
    if (!fallbackView) {
      throw new Error("Sua role nao possui permissao de visualizacao no modulo Escola Biblica.");
    }

    setActiveModule("school");
    setSchoolView(state.view || fallbackView);
    await ensureSchoolInitialized();

    if (state.view === "dashboard" && hasPermission("school_dashboard_view")) {
      await loadDashboardData();
    }
  }

  async function handleLoadError(fn, fallbackMessage) {
    try {
      await fn();
    } catch (error) {
      const message = error instanceof Error ? error.message : fallbackMessage;
      setSchoolMessage(message, true);
    }
  }

  if (el.schoolBtn) {
    el.schoolBtn.addEventListener("click", function () {
      handleLoadError(openSchoolModule, "Falha ao carregar modulo de escola biblica.");
    });
  }

  loadPermissionState();
  applySchoolPermissionLayout();

  if (el.schoolNavCoursesBtn) {
    el.schoolNavCoursesBtn.addEventListener("click", function () {
      setSchoolView("courses");
    });
  }

  if (el.schoolNavClassesBtn) {
    el.schoolNavClassesBtn.addEventListener("click", function () {
      setSchoolView("classes");
    });
  }

  if (el.schoolNavProfessorsBtn) {
    el.schoolNavProfessorsBtn.addEventListener("click", function () {
      setSchoolView("professors");
    });
  }

  if (el.schoolNavLessonsBtn) {
    el.schoolNavLessonsBtn.addEventListener("click", function () {
      setSchoolView("lessons");
    });
  }

  if (el.schoolNavStudentsBtn) {
    el.schoolNavStudentsBtn.addEventListener("click", function () {
      setSchoolView("students");
    });
  }

  if (el.schoolNavAttendanceBtn) {
    el.schoolNavAttendanceBtn.addEventListener("click", function () {
      setSchoolView("attendance");
      // Render the attendance cascading filters
      renderAttendanceCourseOptions();
      renderAttendanceClassOptions();
      renderLessonOptions();
    });
  }

  if (el.schoolNavDashboardBtn) {
    el.schoolNavDashboardBtn.addEventListener("click", function () {
      setSchoolView("dashboard");
      // Load and render the dashboard
      handleLoadError(loadDashboardData, "Falha ao carregar dashboard.");
    });
  }

  if (el.schoolCoursesRefreshBtn) {
    el.schoolCoursesRefreshBtn.addEventListener("click", function () {
      handleLoadError(refreshAll, "Falha ao atualizar cursos.");
    });
  }

  if (el.schoolCoursesAddBtn) {
    el.schoolCoursesAddBtn.addEventListener("click", function () {
      openCourseModal();
    });
  }

  if (el.schoolClassesRefreshBtn) {
    el.schoolClassesRefreshBtn.addEventListener("click", function () {
      handleLoadError(refreshAll, "Falha ao atualizar turmas.");
    });
  }

  if (el.schoolClassesAddBtn) {
    el.schoolClassesAddBtn.addEventListener("click", function () {
      openClassModal();
    });
  }

  if (el.schoolProfessorsRefreshBtn) {
    el.schoolProfessorsRefreshBtn.addEventListener("click", function () {
      handleLoadError(refreshAll, "Falha ao atualizar professores.");
    });
  }

  if (el.schoolProfessorsAddBtn) {
    el.schoolProfessorsAddBtn.addEventListener("click", function () {
      openProfessorModal();
    });
  }

  if (el.schoolLessonsRefreshBtn) {
    el.schoolLessonsRefreshBtn.addEventListener("click", function () {
      handleLoadError(refreshAll, "Falha ao atualizar aulas.");
    });
  }

  if (el.schoolLessonsAddBtn) {
    el.schoolLessonsAddBtn.addEventListener("click", function () {
      openLessonModal();
    });
  }

  if (el.schoolStudentsRefreshBtn) {
    el.schoolStudentsRefreshBtn.addEventListener("click", function () {
      handleLoadError(loadStudents, "Falha ao atualizar alunos.");
    });
  }

  if (el.schoolStudentsAddBtn) {
    el.schoolStudentsAddBtn.addEventListener("click", function () {
      openStudentModal();
    });
  }

  if (el.schoolAttendanceRefreshBtn) {
    el.schoolAttendanceRefreshBtn.addEventListener("click", function () {
      handleLoadError(refreshAll, "Falha ao atualizar chamada.");
    });
  }

  if (el.schoolAttendanceLoadBtn) {
    el.schoolAttendanceLoadBtn.addEventListener("click", function () {
      const lessonId = Number(valueOr(el.schoolAttendanceLessonId && el.schoolAttendanceLessonId.value, ""));
      handleLoadError(function () {
        return loadAttendanceByLesson(lessonId);
      }, "Falha ao carregar chamada.");
    });
  }

  if (el.schoolAttendanceSaveBtn) {
    el.schoolAttendanceSaveBtn.addEventListener("click", function () {
      handleLoadError(saveAttendance, "Falha ao salvar chamada.");
    });
  }

  // Attendance cascading filters
  if (el.schoolAttendanceCourseId) {
    el.schoolAttendanceCourseId.addEventListener("change", function () {
      el.schoolAttendanceClassId.value = "";
      el.schoolAttendanceLessonId.value = "";
      renderAttendanceClassOptions();
      renderLessonOptions();
      el.schoolAttendanceBody.innerHTML = '<tr><td colspan="3">Selecione um curso, turma e aula para iniciar a chamada.</td></tr>';
    });
  }

  if (el.schoolAttendanceClassId) {
    el.schoolAttendanceClassId.addEventListener("change", function () {
      el.schoolAttendanceLessonId.value = "";
      renderLessonOptions();
      el.schoolAttendanceBody.innerHTML = '<tr><td colspan="3">Selecione um curso, turma e aula para iniciar a chamada.</td></tr>';
    });
  }

  // Dashboard filter events
  if (el.schoolDashboardRefreshBtn) {
    el.schoolDashboardRefreshBtn.addEventListener("click", function () {
      handleLoadError(renderDashboardStats, "Falha ao atualizar dashboard.");
    });
  }

  if (el.schoolDashboardCourseId) {
    el.schoolDashboardCourseId.addEventListener("change", function () {
      el.schoolDashboardClassId.value = "";
      renderDashboardClassOptions();
      renderDashboardStats();
    });
  }

  if (el.schoolDashboardClassId) {
    el.schoolDashboardClassId.addEventListener("change", function () {
      renderDashboardStats();
    });
  }

  if (el.schoolDashboardMinPercentage) {
    el.schoolDashboardMinPercentage.addEventListener("change", function () {
      renderDashboardStats();
    });
  }

  // Course modal events
  if (el.schoolCourseForm) {
    el.schoolCourseForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleLoadError(function () {
        return submitCourseForm(event);
      }, "Falha ao salvar curso.");
    });
  }

  if (el.schoolCourseSaveBtn) {
    el.schoolCourseSaveBtn.addEventListener("click", function () {
      if (el.schoolCourseForm) el.schoolCourseForm.dispatchEvent(new Event("submit"));
    });
  }

  if (el.schoolCourseCancelBtn) {
    el.schoolCourseCancelBtn.addEventListener("click", closeCourseModal);
  }

  if (el.schoolCourseModalCloseBtn) {
    el.schoolCourseModalCloseBtn.addEventListener("click", closeCourseModal);
  }

  if (el.schoolCourseDeleteBtn) {
    el.schoolCourseDeleteBtn.addEventListener("click", function () {
      const courseId = Number(valueOr(el.schoolCourseId && el.schoolCourseId.value, ""));
      if (courseId) {
        openDeleteModal("course", courseId);
      }
    });
  }

  // Class modal events
  if (el.schoolClassForm) {
    el.schoolClassForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleLoadError(function () {
        return submitClassForm(event);
      }, "Falha ao salvar turma.");
    });
  }

  if (el.schoolClassSaveBtn) {
    el.schoolClassSaveBtn.addEventListener("click", function () {
      if (el.schoolClassForm) el.schoolClassForm.dispatchEvent(new Event("submit"));
    });
  }

  if (el.schoolClassCancelBtn) {
    el.schoolClassCancelBtn.addEventListener("click", closeClassModal);
  }

  if (el.schoolClassModalCloseBtn) {
    el.schoolClassModalCloseBtn.addEventListener("click", closeClassModal);
  }

  if (el.schoolClassDeleteBtn) {
    el.schoolClassDeleteBtn.addEventListener("click", function () {
      const classId = Number(valueOr(el.schoolClassId && el.schoolClassId.value, ""));
      if (classId) {
        openDeleteModal("class", classId);
      }
    });
  }

  // Professor modal events
  if (el.schoolProfessorForm) {
    el.schoolProfessorForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleLoadError(function () {
        return submitProfessorForm(event);
      }, "Falha ao salvar professor.");
    });
  }

  if (el.schoolProfessorSaveBtn) {
    el.schoolProfessorSaveBtn.addEventListener("click", function () {
      if (el.schoolProfessorForm) el.schoolProfessorForm.dispatchEvent(new Event("submit"));
    });
  }

  if (el.schoolProfessorCancelBtn) {
    el.schoolProfessorCancelBtn.addEventListener("click", closeProfessorModal);
  }

  if (el.schoolProfessorModalCloseBtn) {
    el.schoolProfessorModalCloseBtn.addEventListener("click", closeProfessorModal);
  }

  if (el.schoolProfessorDeleteBtn) {
    el.schoolProfessorDeleteBtn.addEventListener("click", function () {
      const professorId = Number(valueOr(el.schoolProfessorId && el.schoolProfessorId.value, ""));
      if (professorId) {
        openDeleteModal("professor", professorId);
      }
    });
  }

  // Lesson modal events
  if (el.schoolLessonForm) {
    el.schoolLessonForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleLoadError(function () {
        return submitLessonForm(event);
      }, "Falha ao salvar aula.");
    });
  }

  if (el.schoolLessonSaveBtn) {
    el.schoolLessonSaveBtn.addEventListener("click", function () {
      if (el.schoolLessonForm) el.schoolLessonForm.dispatchEvent(new Event("submit"));
    });
  }

  if (el.schoolLessonCancelBtn) {
    el.schoolLessonCancelBtn.addEventListener("click", closeLessonModal);
  }

  if (el.schoolLessonModalCloseBtn) {
    el.schoolLessonModalCloseBtn.addEventListener("click", closeLessonModal);
  }

  if (el.schoolLessonDeleteBtn) {
    el.schoolLessonDeleteBtn.addEventListener("click", function () {
      const lessonId = Number(valueOr(el.schoolLessonId && el.schoolLessonId.value, ""));
      if (lessonId) {
        openDeleteModal("lesson", lessonId);
      }
    });
  }

  // Student modal events
  if (el.schoolStudentForm) {
    el.schoolStudentForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleLoadError(function () {
        return submitStudentForm(event);
      }, "Falha ao salvar aluno.");
    });
  }

  if (el.schoolStudentSaveBtn) {
    el.schoolStudentSaveBtn.addEventListener("click", function () {
      if (el.schoolStudentForm) el.schoolStudentForm.dispatchEvent(new Event("submit"));
    });
  }

  if (el.schoolStudentCancelBtn) {
    el.schoolStudentCancelBtn.addEventListener("click", closeStudentModal);
  }

  if (el.schoolStudentModalCloseBtn) {
    el.schoolStudentModalCloseBtn.addEventListener("click", closeStudentModal);
  }

  if (el.schoolStudentDeleteBtn) {
    el.schoolStudentDeleteBtn.addEventListener("click", function () {
      const studentId = Number(valueOr(el.schoolStudentId && el.schoolStudentId.value, ""));
      if (studentId) {
        openDeleteModal("student", studentId);
      }
    });
  }

  if (el.schoolDeleteConfirmBtn) {
    el.schoolDeleteConfirmBtn.addEventListener("click", function () {
      handleLoadError(confirmDeleteModal, "Falha ao excluir registro.");
    });
  }

  if (el.schoolDeleteCancelBtn) {
    el.schoolDeleteCancelBtn.addEventListener("click", closeDeleteModal);
  }

  if (el.schoolDeleteModalCloseBtn) {
    el.schoolDeleteModalCloseBtn.addEventListener("click", closeDeleteModal);
  }

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      closeAllSchoolModals();
    }
  });

  document.addEventListener("click", function (event) {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    if (isSchoolModalOverlay(target)) {
      closeAllSchoolModals();
    }
  });

  if (el.schoolCoursesBody) {
    el.schoolCoursesBody.addEventListener("click", function (event) {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      const courseId = Number(target.getAttribute("data-course-edit"));
      const courseDeleteId = Number(target.getAttribute("data-course-delete"));
      if (courseId) {
        openCourseModal(courseId);
      } else if (courseDeleteId) {
        openDeleteModal("course", courseDeleteId);
      }
    });
  }

  if (el.schoolClassesBody) {
    el.schoolClassesBody.addEventListener("click", function (event) {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      const classId = Number(target.getAttribute("data-class-edit"));
      const classDeleteId = Number(target.getAttribute("data-class-delete"));
      if (classId) {
        openClassModal(classId);
      } else if (classDeleteId) {
        openDeleteModal("class", classDeleteId);
      }
    });
  }
  if (el.schoolProfessorsBody) {
    el.schoolProfessorsBody.addEventListener("click", function (event) {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      const professorId = Number(target.getAttribute("data-professor-edit"));
      const professorDeleteId = Number(target.getAttribute("data-professor-delete"));
      if (professorId) {
        openProfessorModal(professorId);
      } else if (professorDeleteId) {
        openDeleteModal("professor", professorDeleteId);
      }
    });
  }

  if (el.schoolLessonsBody) {
    el.schoolLessonsBody.addEventListener("click", function (event) {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      const lessonId = Number(target.getAttribute("data-lesson-edit"));
      const lessonDeleteId = Number(target.getAttribute("data-lesson-delete"));
      if (lessonId) {
        openLessonModal(lessonId);
      } else if (lessonDeleteId) {
        openDeleteModal("lesson", lessonDeleteId);
      }
    });
  }

  if (el.schoolStudentsBody) {
    el.schoolStudentsBody.addEventListener("click", function (event) {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      const studentId = Number(target.getAttribute("data-student-edit"));
      const studentDeleteId = Number(target.getAttribute("data-student-delete"));
      if (studentId) {
        openStudentModal(studentId);
      } else if (studentDeleteId) {
        openDeleteModal("student", studentDeleteId);
      }
    });
  }
})();
