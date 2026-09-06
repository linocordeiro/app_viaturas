/**
 * Frontline PF — JavaScript para interatividade de UI
 * Sistema APP_VIATURAS
 */

document.addEventListener('DOMContentLoaded', function () {
  // Auto-dismiss de mensagens de alerta após 5 segundos
  const alerts = document.querySelectorAll('.pf-alert');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = 'opacity 0.5s ease';
      alert.style.opacity = '0';
      setTimeout(function () {
        if (alert.parentNode) {
          alert.parentNode.removeChild(alert);
        }
      }, 500);
    }, 6000);
  });

  // Confirmação antes de encerrar ficha
  const encerramentoForms = document.querySelectorAll('.form-encerrar-ficha');
  encerramentoForms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!confirm('ATENÇÃO: Ao encerrar a ficha do expediente, não será mais permitido editar nem incluir novos registros de viaturas. Deseja realmente encerrar?')) {
        e.preventDefault();
      }
    });
  });
});
