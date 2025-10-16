// Función para mostrar notificaciones
function showNotification(message, type) {
  const notification = document.getElementById("notification");
  notification.textContent = message;
  notification.className = `notification ${type} show`;

  setTimeout(() => {
    notification.classList.remove("show");
  }, 4000);
}

// Función para vista previa de PDF
function previewPDF(documentoId) {
  const pdfFrame = document.getElementById("pdfFrame");
  const pdfViewerModal = document.getElementById("pdfViewerModal");
  const pdfViewerTitle = document.getElementById("pdfViewerTitle");

  // Aquí deberías tener una URL para obtener el PDF
  // Por ahora, usaremos una URL placeholder
  pdfFrame.src = `/documentos/${documentoId}/preview/`;
  pdfViewerTitle.textContent = "Cargando documento...";
  pdfViewerModal.style.display = "flex";

  // Cuando el PDF cargue, actualizar el título
  pdfFrame.onload = function () {
    // Obtener el nombre del documento del elemento correspondiente
    const docElement = document
      .querySelector(`[onclick="previewPDF(${documentoId})"]`)
      .closest(".document-item");
    const docName = docElement.querySelector(".document-name").textContent;
    pdfViewerTitle.textContent = docName;
  };
}

// Función para cerrar el visor de PDF
function closePDFViewer() {
  document.getElementById("pdfViewerModal").style.display = "none";
  document.getElementById("pdfFrame").src = "";
}

// Funcionalidad de búsqueda
document
  .getElementById("searchButton")
  .addEventListener("click", performSearch);
document
  .getElementById("searchInput")
  .addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      performSearch();
    }
  });

function performSearch() {
  const searchTerm = document
    .getElementById("searchInput")
    .value.toLowerCase()
    .trim();
  const categoryCards = document.querySelectorAll(".category-card");
  let foundResults = false;

  categoryCards.forEach((card) => {
    const documents = card.querySelectorAll(".document-item");
    let categoryHasResults = false;

    documents.forEach((doc) => {
      const docName = doc.getAttribute("data-name");
      const docDesc = doc.getAttribute("data-desc");

      if (docName.includes(searchTerm) || docDesc.includes(searchTerm)) {
        doc.style.display = "flex";
        categoryHasResults = true;
        foundResults = true;
      } else {
        doc.style.display = "none";
      }
    });

    // Mostrar/ocultar categorías según si tienen resultados
    if (categoryHasResults || searchTerm === "") {
      card.style.display = "block";
    } else {
      card.style.display = "none";
    }
  });

  if (searchTerm && !foundResults) {
    showNotification(
      "No se encontraron documentos que coincidan con la búsqueda",
      "error"
    );
  }
}

// Cerrar modal al hacer clic fuera
document
  .getElementById("pdfViewerModal")
  .addEventListener("click", function (e) {
    if (e.target === this) {
      closePDFViewer();
    }
  });

// Animación de entrada
// En el JavaScript, cambia la función para usar event listeners
document.addEventListener("DOMContentLoaded", function () {
  // Agregar event listeners a todos los botones de vista previa
  document.querySelectorAll(".preview-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const docId = this.getAttribute("data-doc-id");
      previewPDF(docId);
    });
  });
});

// Modifica la función previewPDF para ser más robusta
function previewPDF(documentoId) {
  // Validar que documentoId sea un número válido
  if (!documentoId || isNaN(documentoId)) {
    showNotification("Error: ID de documento inválido", "error");
    return;
  }

  const pdfFrame = document.getElementById("pdfFrame");
  const pdfViewerModal = document.getElementById("pdfViewerModal");
  const pdfViewerTitle = document.getElementById("pdfViewerTitle");

  // Mostrar loading
  pdfViewerTitle.textContent = "Cargando documento...";
  pdfViewerModal.style.display = "flex";

  // Construir la URL correctamente
  pdfFrame.src = `/documentos/${documentoId}/preview/`;

  // Encontrar el nombre del documento
  const docElement = document
    .querySelector(`[data-doc-id="${documentoId}"]`)
    .closest(".document-item");
  if (docElement) {
    const docName = docElement.querySelector(".document-name").textContent;
    pdfViewerTitle.textContent = docName;
  }
}
