---
trigger: always_on
---

# Padrão Obrigatório de Botões de Ação em Tabelas

Em todas as tabelas atuais e futuras do projeto:
1. **Somente Ícone (Sem Texto)**: Os botões da coluna de ações NUNCA devem conter texto visível, apenas o ícone do FontAwesome centralizado.
2. **Acessibilidade**: Devem obrigatoriamente conter os atributos `title="..."` e `aria-label="..."` detalhando a ação ao operador.
3. **Container Oficial**: As ações na linha da tabela devem ser dispostas dentro de:
   ```html
   <td style="text-align: right; white-space: nowrap;">
     <div class="pf-table-actions">
       <!-- botões aqui -->
     </div>
   </td>
   ```
4. **Identidade Visual Semântica Frontline PF**:
   - **Visualizar / Detalhes / Acessar**: `.pf-action-btn.pf-action-view` (Azul PF `#3363CC`) com `fas fa-eye` ou `fas fa-folder-open`.
   - **Editar / Modificar**: `.pf-action-btn.pf-action-edit` (Dourado PF `#E1AD62`) com `fas fa-edit`.
   - **Operação Positiva / Retorno / Concluir**: `.pf-action-btn.pf-action-success` (Verde PF `#33A841`) com `fas fa-sign-in-alt` ou `fas fa-check`.
   - **Manutenção / Serviços**: `.pf-action-btn.pf-action-service` (Dourado/Âmbar PF) com `fas fa-tools`.
   - **Excluir / Desativar / Bloquear**: `.pf-action-btn.pf-action-danger` (Vermelho PF `#BF0C1D`) com `fas fa-trash-alt` ou `fas fa-user-slash`.
   - **Ativar Usuário / Registro**: `.pf-action-btn.pf-action-success` com `fas fa-user-check`.
   - **Exportar PDF**: `.pf-action-btn.pf-action-pdf` (Vermelho PF) com `fas fa-file-pdf`.
   - **Exportar Excel**: `.pf-action-btn.pf-action-excel` (Verde PF) com `fas fa-file-excel`.
