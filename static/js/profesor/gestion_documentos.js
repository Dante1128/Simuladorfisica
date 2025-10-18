// ============================================================
//  GESTIÓN DE DOCUMENTOS - SISTEMA SEGURO Y OPTIMIZADO
// ============================================================

// Obtener token CSRF (para Django)
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie("csrftoken");

document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ Panel de gestión de documentos inicializado");

  // ============================================================
  //  VARIABLES GLOBALES
  // ============================================================
  let currentEditingDocId = null;
  let documentToDelete = { id: null, name: null };

  // ============================================================
  //  ELEMENTOS DEL DOM (SEGURIDAD: solo si existen)
  // ============================================================
  const editButtons = document.querySelectorAll(".btn-edit");
  const deleteButtons = document.querySelectorAll(".btn-delete");
  const newDocButton = document.getElementById("newDoc");
  const emptyNewDocButton = document.getElementById("emptyNewDoc");
  const modal = document.getElementById("docModal");
  const modalTitle = document.getElementById("modalTitle");
  const docNameInput = document.getElementById("docName");
  const docStatusSelect = document.getElementById("docStatus");
  const docDescripcionTextarea = document.getElementById("docDescripcion");
  const docPdfInput = document.getElementById("docPdf");
  const cancelBtn = document.getElementById("cancelBtn");
  const saveBtn = document.getElementById("saveBtn");
  const notification = document.getElementById("notification");
  const helpBtn = document.getElementById("helpBtn");
  const helpPanel = document.getElementById("helpPanel");
  const closeHelp = document.getElementById("closeHelp");
  const searchInput = document.querySelector(".search-input");
  const mainSearchInput = document.getElementById("mainSearchInput");
  const mainSearchButton = document.getElementById("mainSearchButton");
  const documentoForm = document.getElementById("documentoForm");
  const documentsGrid = document.getElementById("documentsGrid");
  const confirmModal = document.getElementById("confirmModal");
  const confirmMessage = document.getElementById("confirmMessage");
  const cancelDeleteBtn = document.getElementById("cancelDeleteBtn");
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
  const sidebar = document.getElementById("sidebar");
  const toggleSidebar = document.getElementById("toggleSidebar");
  const dashboardContainer = document.querySelector(".dashboard-container");

  // ============================================================
  //  FUNCIONES DE UTILIDAD
  // ============================================================
  function showNotification(message, type) {
    if (!notification) return;
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.add("show");

    setTimeout(() => {
      notification.classList.remove("show");
    }, 4000);
  }

  function openModal(isNew = false, docData = null) {
    if (!modal) return;

    if (isNew) {
      modalTitle.textContent = "Nuevo Documento";
      docNameInput.value = "";
      docStatusSelect.value = "Activo";
      docDescripcionTextarea.value = "";
      docPdfInput.value = "";
      currentEditingDocId = null;
      
      // Ocultar información de archivo actual en nuevo documento
      const currentFileInfo = document.getElementById('currentFileInfo');
      if (currentFileInfo) currentFileInfo.style.display = 'none';
    } else {
      modalTitle.textContent = "Editar Documento";
      docNameInput.value = docData.nombre || "";
      docStatusSelect.value = docData.estado || "Activo";
      docDescripcionTextarea.value = docData.descripcion || "";
      currentEditingDocId = docData.id;
      
      // Mostrar archivo actual si existe
      if (docData.nombreArchivo) {
        mostrarArchivoActual(docData.nombreArchivo, docData.tamaño);
      } else {
        // Ocultar si no hay archivo
        const currentFileInfo = document.getElementById('currentFileInfo');
        if (currentFileInfo) currentFileInfo.style.display = 'none';
      }
    }
    modal.style.display = "flex";
  }

  function mostrarArchivoActual(nombreArchivo, tamaño) {
    const currentFileInfo = document.getElementById('currentFileInfo');
    const currentFileName = document.getElementById('currentFileName');
    const currentFileSize = document.getElementById('currentFileSize');
    
    if (nombreArchivo && currentFileInfo && currentFileName && currentFileSize) {
      currentFileName.textContent = nombreArchivo;
      currentFileSize.textContent = tamaño ? `(${tamaño})` : '';
      currentFileInfo.style.display = 'block';
    }
  }

  // Función para extraer información del PDF de la tarjeta del documento
  function extraerInfoPDF(docCard) {
    const pdfInfo = docCard.querySelector('.pdf-info');
    if (!pdfInfo) return { nombreArchivo: null, tamaño: null };
    
    const pdfText = pdfInfo.textContent.trim();
    
    if (pdfText.includes("No hay PDF")) {
      return { nombreArchivo: null, tamaño: null };
    }
    
    // Extraer nombre y tamaño del texto existente
    let nombreArchivo = "Documento PDF";
    let tamaño = "";
    
    // Buscar el texto entre <i class="fas fa-file-pdf"></i> y el tamaño entre paréntesis
    const textoLimpio = pdfText.replace(/<i class="fas fa-file-pdf"><\/i>/, '').trim();
    const match = textoLimpio.match(/(.+?)\s*(?:\(([^)]+)\))?$/);
    
    if (match) {
      nombreArchivo = match[1].trim();
      if (match[2]) {
        tamaño = match[2].trim();
      }
    }
    
    return { nombreArchivo, tamaño };
  }

  function closeModal() {
    if (!modal) return;
    modal.style.display = "none";
    if (documentoForm) documentoForm.reset();
  }

  async function guardarDocumento(event) {
    if (event) event.preventDefault();

    const nombre = docNameInput?.value.trim();
    const estado = docStatusSelect?.value;
    const descripcion = docDescripcionTextarea?.value;
    const archivo = docPdfInput?.files[0];
    const removeCurrentFile = document.getElementById('removeCurrentFileFlag')?.value === 'true';

    if (!nombre) {
      showNotification("El nombre del documento no puede estar vacío", "error");
      return;
    }

    if (archivo) {
      if (archivo.type !== "application/pdf") {
        showNotification("Solo se permiten archivos PDF", "error");
        return;
      }

      if (archivo.size > 10 * 1024 * 1024) {
        showNotification("El archivo es demasiado grande (máx. 10MB)", "error");
        return;
      }
    }

    try {
      const formData = new FormData();
      formData.append("action", currentEditingDocId ? "editar" : "crear");
      formData.append("nombre", nombre);
      formData.append("estado", estado);
      formData.append("descripcion", descripcion);
      formData.append("categoria", "fisica_general");
      
      if (currentEditingDocId) {
        formData.append("id", currentEditingDocId);
        // Añadir flag para eliminar archivo actual si se presionó "Quitar"
        if (removeCurrentFile) {
          formData.append("remove_current_file", "true");
        }
      }
      
      if (archivo) formData.append("archivo_pdf", archivo);

      showNotification("Guardando documento...", "success");

      const response = await fetch("", {
        method: "POST",
        headers: {
          "X-CSRFToken": csrftoken,
          "X-Requested-With": "XMLHttpRequest",
        },
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        showNotification("✓ " + result.message, "success");
        setTimeout(() => {
          closeModal();
          location.reload();
        }, 1500);
      } else {
        showNotification("✗ Error: " + result.error, "error");
      }
    } catch (error) {
      console.error("Error:", error);
      showNotification("✗ Error de conexión: " + error.message, "error");
    }
  }

  // ============================================================
  //  SIDEBAR (Guardar estado de colapso)
  // ============================================================
  function toggleSidebarFunc() {
    if (!sidebar || !dashboardContainer) return;
    sidebar.classList.toggle("collapsed");
    dashboardContainer.classList.toggle("collapsed");

    const isCollapsed = sidebar.classList.contains("collapsed");
    localStorage.setItem("sidebarCollapsed", isCollapsed);
  }

  if (toggleSidebar) toggleSidebar.addEventListener("click", toggleSidebarFunc);

  const savedState = localStorage.getItem("sidebarCollapsed");
  if (savedState === "true" && sidebar && dashboardContainer) {
    sidebar.classList.add("collapsed");
    dashboardContainer.classList.add("collapsed");
  }

  // ============================================================
  //  EVENTOS DE MODAL
  // ============================================================
  if (newDocButton) newDocButton.addEventListener("click", () => openModal(true));
  if (emptyNewDocButton) emptyNewDocButton.addEventListener("click", () => openModal(true));
  if (cancelBtn) cancelBtn.addEventListener("click", closeModal);
  if (saveBtn) saveBtn.addEventListener("click", guardarDocumento);
  if (documentoForm) documentoForm.addEventListener("submit", guardarDocumento);

  // ============================================================
  //  EVENTOS DE EDICIÓN Y ELIMINACIÓN
  // ============================================================
  editButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const docId = this.getAttribute("data-id");
      const docCard = this.closest(".document-card");
      const docNombre = docCard.querySelector(".doc-title").textContent;
      const docEstado = docCard.querySelector(".doc-status span").textContent;
      const descElement = docCard.querySelector(".doc-description");
      const docDescripcion = descElement ? descElement.textContent : "";
      const pdfInfo = extraerInfoPDF(docCard);
        
      const docData = {
        id: docId,
        nombre: docNombre,
        estado: docEstado,
        descripcion: docDescripcion,
        nombreArchivo: pdfInfo.nombreArchivo,
        tamaño: pdfInfo.tamaño
      };
      
      openModal(false, docData);
    });
  });

  deleteButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const docId = this.getAttribute("data-id");
      const docNombre = this.closest(".document-card").querySelector(".doc-title").textContent;
      documentToDelete = { id: docId, name: docNombre };
      showConfirmModal(docNombre);
    });
  });

  // ============================================================
  //  MANEJO DE BOTÓN "QUITAR" ARCHIVO ACTUAL
  // ============================================================
  const removeCurrentFileBtn = document.getElementById('removeCurrentFile');
  if (removeCurrentFileBtn) {
    removeCurrentFileBtn.addEventListener('click', function() {
      const currentFileInfo = document.getElementById('currentFileInfo');
      if (currentFileInfo) {
        currentFileInfo.style.display = 'none';
      }
      document.getElementById('removeCurrentFileFlag').value = 'true';
    });
  }

  // ============================================================
  //  MODAL DE CONFIRMACIÓN
  // ============================================================
  function showConfirmModal(docName) {
    if (!confirmModal) return;
    confirmMessage.textContent = `¿Está seguro de que desea eliminar "${docName}"? Esta acción no se puede deshacer.`;
    confirmModal.style.display = "flex";
  }

  function closeConfirmModal() {
    if (confirmModal) confirmModal.style.display = "none";
    documentToDelete = { id: null, name: null };
  }

  if (cancelDeleteBtn) cancelDeleteBtn.addEventListener("click", closeConfirmModal);
  if (confirmDeleteBtn)
    confirmDeleteBtn.addEventListener("click", function () {
      if (documentToDelete.id && documentToDelete.name) {
        eliminarDocumento(documentToDelete.id, documentToDelete.name);
        closeConfirmModal();
      }
    });

  window.addEventListener("click", (e) => {
    if (e.target === confirmModal) closeConfirmModal();
    if (e.target === modal) closeModal();
  });

  async function eliminarDocumento(id, nombre) {
    try {
      showNotification(`Eliminando "${nombre}"...`, "success");

      const response = await fetch("", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
          action: "eliminar",
          id: id,
        }),
      });

      const result = await response.json();

      if (result.success) {
        showNotification(`✓ "${nombre}" eliminado correctamente`, "success");
        setTimeout(() => location.reload(), 1500);
      } else {
        showNotification("✗ Error al eliminar: " + result.error, "error");
      }
    } catch (error) {
      showNotification("✗ Error de conexión", "error");
    }
  }

  // ============================================================
  //  MANEJO DE ARCHIVOS PDF
  // ============================================================
  if (docPdfInput) {
    docPdfInput.addEventListener("change", function () {
      const fileName = this.files[0] ? this.files[0].name : "No se seleccionó archivo";
      const fileSize = this.files[0]
        ? (this.files[0].size / 1024 / 1024).toFixed(2) + " MB"
        : "";
      let fileInfo = document.getElementById("fileInfo");
      if (!fileInfo) {
        fileInfo = document.createElement("div");
        fileInfo.id = "fileInfo";
        docPdfInput.parentNode.appendChild(fileInfo);
      }
      fileInfo.innerHTML = `<small style="color: #27ae60;"><i class="fas fa-file-pdf"></i> ${fileName} (${fileSize})</small>`;
    });
  }

  // ============================================================
  //  PANEL DE AYUDA
  // ============================================================
  if (helpBtn && helpPanel) {
    helpBtn.addEventListener("click", () => (helpPanel.style.display = "block"));
  }
  if (closeHelp && helpPanel) {
    closeHelp.addEventListener("click", () => (helpPanel.style.display = "none"));
  }

  // ============================================================
  //  BÚSQUEDA DE DOCUMENTOS
  // ============================================================
  function performSearch() {
    const searchText = mainSearchInput?.value.trim().toLowerCase() || "";
    const cards = document.querySelectorAll(".document-card");
    let visibleCount = 0;

    cards.forEach((card) => {
      const text = card.textContent.toLowerCase();
      const shouldShow = text.includes(searchText);
      card.style.display = shouldShow ? "flex" : "none";
      if (shouldShow) visibleCount++;
    });

    if (searchText) {
      showNotification(`Encontrados ${visibleCount} documentos para: "${searchText}"`, "success");
    }
  }

  if (mainSearchInput)
    mainSearchInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") performSearch();
    });

  if (mainSearchButton) mainSearchButton.addEventListener("click", performSearch);

  if (searchInput)
    searchInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        const searchText = searchInput.value.trim().toLowerCase();
        showNotification(`Búsqueda del header: "${searchText}"`, "success");
      }
    });

  function clearSearch() {
    if (!mainSearchInput) return;
    mainSearchInput.value = "";
    document.querySelectorAll(".document-card").forEach((card) => {
      card.style.display = "flex";
    });
    showNotification("Búsqueda limpiada", "success");
  }
});