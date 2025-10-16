// CSRF Token para Django
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

// Variables globales
let currentEditingDocId = null;

// Elementos del DOM
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
const searchInput = document.querySelector('.search-input'); // Búsqueda del header
const mainSearchInput = document.getElementById('mainSearchInput'); // Búsqueda principal
const mainSearchButton = document.getElementById('mainSearchButton'); // Botón de búsqueda principal
const documentoForm = document.getElementById("documentoForm");
const documentsGrid = document.getElementById("documentsGrid");

// Variables para el sidebar
const sidebar = document.getElementById('sidebar');
const toggleSidebar = document.getElementById('toggleSidebar');
const dashboardContainer = document.querySelector('.dashboard-container');

// Función para toggle del sidebar
function toggleSidebarFunc() {
    sidebar.classList.toggle('collapsed');
    dashboardContainer.classList.toggle('collapsed');
    
    // Guardar estado en localStorage
    const isCollapsed = sidebar.classList.contains('collapsed');
    localStorage.setItem('sidebarCollapsed', isCollapsed);
}

// Event listener para el botón de toggle
toggleSidebar.addEventListener('click', toggleSidebarFunc);

// Cargar estado del sidebar al iniciar
document.addEventListener('DOMContentLoaded', function() {
    const savedState = localStorage.getItem('sidebarCollapsed');
    if (savedState === 'true') {
        sidebar.classList.add('collapsed');
        dashboardContainer.classList.add('collapsed');
    }
});

// Funciones de utilidad
function showNotification(message, type) {
  notification.textContent = message;
  notification.className = `notification ${type}`;
  notification.classList.add("show");

  setTimeout(() => {
    notification.classList.remove("show");
  }, 4000);
}

function openModal(
  isNew = false,
  docName = "",
  docStatus = "Activo",
  docDescripcion = ""
) {
  if (isNew) {
    modalTitle.textContent = "Nuevo Documento";
    docNameInput.value = "";
    docStatusSelect.value = "Activo";
    docDescripcionTextarea.value = "";
    docPdfInput.value = ""; // Limpiar archivo
    currentEditingDocId = null;
  } else {
    modalTitle.textContent = "Editar Documento";
    docNameInput.value = docName;
    docStatusSelect.value = docStatus;
    docDescripcionTextarea.value = docDescripcion;
    docPdfInput.value = ""; // No mostrar archivo existente por seguridad
  }
  modal.style.display = "flex";
}

function closeModal() {
  modal.style.display = "none";
  // Limpiar formulario
  documentoForm.reset();
}

// Nueva función para guardar con archivo PDF
async function guardarDocumento(event) {
  if (event) event.preventDefault();

  const nombre = docNameInput.value.trim();
  const estado = docStatusSelect.value;
  const descripcion = docDescripcionTextarea.value;
  const archivo = docPdfInput.files[0];

  if (!nombre) {
    showNotification("El nombre del documento no puede estar vacío", "error");
    return;
  }

  // Validar archivo si se seleccionó
  if (archivo) {
    if (archivo.type !== "application/pdf") {
      showNotification("Solo se permiten archivos PDF", "error");
      return;
    }

    if (archivo.size > 10 * 1024 * 1024) {
      // 10MB
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
    }

    if (archivo) {
      formData.append("archivo_pdf", archivo);
    }

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

// Event Listeners
newDocButton.addEventListener("click", () => {
  openModal(true);
});

if (emptyNewDocButton) {
  emptyNewDocButton.addEventListener("click", () => {
    openModal(true);
  });
}

editButtons.forEach((button) => {
  button.addEventListener("click", function () {
    const docId = this.getAttribute("data-id");
    const docCard = this.closest(".document-card");
    const docNombre = docCard.querySelector(".doc-title").textContent;
    const docEstado = docCard.querySelector(".doc-status span").textContent;

    // Obtener descripción
    const descElement = docCard.querySelector(".doc-description");
    const docDescripcion = descElement ? descElement.textContent : "";

    currentEditingDocId = docId;
    openModal(false, docNombre, docEstado, docDescripcion);
  });
});

// Variables para el modal de confirmación
const confirmModal = document.getElementById('confirmModal');
const confirmMessage = document.getElementById('confirmMessage');
const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
let documentToDelete = { id: null, name: null };

// Event listeners para botones de eliminar
deleteButtons.forEach(button => {
    button.addEventListener('click', function() {
        const docId = this.getAttribute('data-id');
        const docNombre = this.closest('.document-card').querySelector('.doc-title').textContent;
        
        // Guardar información del documento a eliminar
        documentToDelete.id = docId;
        documentToDelete.name = docNombre;
        
        // Mostrar modal de confirmación
        showConfirmModal(docNombre);
    });
});

// Función para mostrar el modal de confirmación
function showConfirmModal(docName) {
    confirmMessage.textContent = `¿Está seguro de que desea eliminar "${docName}"? Esta acción no se puede deshacer.`;
    confirmModal.style.display = 'flex';
}

// Función para cerrar el modal de confirmación
function closeConfirmModal() {
    confirmModal.style.display = 'none';
    documentToDelete = { id: null, name: null };
}

// Event listeners para los botones del modal de confirmación
cancelDeleteBtn.addEventListener('click', closeConfirmModal);

confirmDeleteBtn.addEventListener('click', function() {
    if (documentToDelete.id && documentToDelete.name) {
        eliminarDocumento(documentToDelete.id, documentToDelete.name);
        closeConfirmModal();
    }
});

// Cerrar modal al hacer clic fuera
window.addEventListener('click', (e) => {
    if (e.target === confirmModal) {
        closeConfirmModal();
    }
});

async function eliminarDocumento(id, nombre) {
    try {
        showNotification(`Eliminando "${nombre}"...`, 'success');
        
        const response = await fetch('', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                action: 'eliminar',
                id: id
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`✓ "${nombre}" eliminado correctamente`, 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            showNotification('✗ Error al eliminar: ' + result.error, 'error');
        }
    } catch (error) {
        showNotification('✗ Error de conexión', 'error');
    }
}

// Event listeners actualizados
cancelBtn.addEventListener("click", closeModal);
saveBtn.addEventListener("click", guardarDocumento);
documentoForm.addEventListener("submit", guardarDocumento);

// Mejorar la experiencia del input de archivo
docPdfInput.addEventListener("change", function () {
  const fileName = this.files[0]
    ? this.files[0].name
    : "No se seleccionó archivo";
  const fileSize = this.files[0]
    ? (this.files[0].size / 1024 / 1024).toFixed(2) + " MB"
    : "";

  // Mostrar información del archivo
  const fileInfo =
    document.getElementById("fileInfo") || document.createElement("div");
  fileInfo.id = "fileInfo";
  fileInfo.innerHTML = `<small style="color: #27ae60;"><i class="fas fa-file-pdf"></i> ${fileName} (${fileSize})</small>`;

  if (!document.getElementById("fileInfo")) {
    docPdfInput.parentNode.appendChild(fileInfo);
  }
});

// Funcionalidad de ayuda y búsqueda
helpBtn.addEventListener("click", () => {
  helpPanel.style.display = "block";
});

closeHelp.addEventListener("click", () => {
  helpPanel.style.display = "none";
});



// Función de búsqueda común
function performSearch() {
    const searchText = mainSearchInput.value.trim().toLowerCase();
    const cards = document.querySelectorAll('.document-card');
    let visibleCount = 0;
    
    cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        const shouldShow = text.includes(searchText);
        card.style.display = shouldShow ? 'flex' : 'none';
        
        if (shouldShow) visibleCount++;
    });
    
    // Mostrar notificación si hay búsqueda activa
    if (searchText) {
        showNotification(`Encontrados ${visibleCount} documentos para: "${searchText}"`, 'success');
    }
}

// Eventos para la búsqueda principal
mainSearchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        performSearch();
    }
});

mainSearchButton.addEventListener('click', performSearch);

// Evento para la búsqueda del header (opcional)
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const searchText = searchInput.value.trim().toLowerCase();
        showNotification(`Búsqueda del header: "${searchText}"`, 'success');
        // Aquí puedes agregar funcionalidad específica para esta búsqueda
    }
});

// Función para limpiar búsqueda
function clearSearch() {
    mainSearchInput.value = '';
    const cards = document.querySelectorAll('.document-card');
    cards.forEach(card => {
        card.style.display = 'flex';
    });
    showNotification('Búsqueda limpiada', 'success');
}

// Cerrar modal al hacer clic fuera
window.addEventListener("click", (e) => {
  if (e.target === modal) {
    closeModal();
  }
});

// Inicialización
document.addEventListener("DOMContentLoaded", () => {
  console.log("Panel de gestión de documentos inicializado");
});
