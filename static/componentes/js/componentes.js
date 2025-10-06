// pequeño enhacement para form de búsqueda: limpiar si vacio
document.addEventListener('DOMContentLoaded', function(){
  const input = document.querySelector('.search-form input[name="q"]');
  if(!input) return;
  input.addEventListener('keyup', function(ev){
    if(ev.key === 'Escape'){
      input.value = '';
      input.form.submit();
    }
  });
});
