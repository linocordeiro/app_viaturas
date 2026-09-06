# Frontline PF — Guia para Criação de Landing Pages

Este guia estabelece os padrões para desenvolvimento de Landing Pages, portais de serviços ao cidadão, páginas de campanhas institucionais e interfaces públicas da Polícia Federal, unificando a sobriedade do Frontline com o padrão visual Gov.br.

---

## 1. Princípios de Design para Landing Pages

1. **Autoridade Serena e Confiabilidade**: O cidadão precisa identificar imediatamente que está em um ambiente oficial, seguro e auditado da Polícia Federal e do Governo Federal.
2. **Clareza de Ação (Acesso Rápido)**: O objetivo central da página (ex: "Emitir Passaporte", "Certidão de Antecedentes", "Registrar Sinarm") deve estar evidente na primeira dobra (*above the fold*).
3. **Acessibilidade Universal**: Conformidade obrigatória com as diretrizes e-MAG e WCAG 2.1 nível AA (atalhos de teclado, alto contraste, suporte a leitores de tela e widget VLibras).
4. **Alinhamento ao Grid de 8px**: Todo o layout, espaçamentos entre blocos de conteúdo e paddings de cards devem seguir múltiplos de 8px.

---

## 2. Estrutura Padrão de Landing Page da PF

```
+--------------------------------------------------------------+
| 1. Barra de Acessibilidade e Identificação Gov.br            |
+--------------------------------------------------------------+
| 2. Header Institucional (Logo Gov.br + Ministério + Busca)    |
+--------------------------------------------------------------+
| 3. Hero Section (Título do Serviço, Brasão PF, CTA Primário) |
+--------------------------------------------------------------+
| 4. Cards de Destaque / Serviços Principais (Grid de 8px)     |
+--------------------------------------------------------------+
| 5. Passo a Passo do Cidadão (Etapas / Requisitos)            |
+--------------------------------------------------------------+
| 6. Seção de Avisos / Alertas Operacionais                    |
+--------------------------------------------------------------+
| 7. Perguntas Frequentes (FAQ / Accordion)                    |
+--------------------------------------------------------------+
| 8. Canais de Atendimento e Unidades da PF                    |
+--------------------------------------------------------------+
| 9. Rodapé Institucional Gov.br + Brasão e Direitos da PF     |
+--------------------------------------------------------------+
```

---

## 3. Detalhamento das Seções

### 3.1. Barra Gov.br e Header Institucional
- **Fundo**: Branco (`#FFFFFF`) ou Neutro Claro (`#F4F4F4`).
- **Logo Gov.br**: Alinhado à esquerda no topo.
- **Assinatura**: "Ministério da Justiça e Segurança Pública" em fonte regular 12px.
- **Links Obrigatórios de Acessibilidade**: Ir para o conteúdo (Alt+1), Ir para o menu (Alt+2), Ir para a busca (Alt+3), Ir para o rodapé (Alt+4).
- **Contraste e VLibras**: Botão de alternância de alto contraste e botão oficial do VLibras.

### 3.2. Hero Section (Dobra Principal)
A Hero Section deve capturar a atenção com sobriedade e direcionar o cidadão para o serviço:

- **Opção A (Dark Institucional - Alta Solenidade)**:
  - Fundo: **PF-Black (`#111213`)** com sutis detalhes geométricos em **PF-Gold500 (`#E1AD62`)**.
  - Título (`h1`): Roboto Bold 36px na cor branca (`#FFFFFF`).
  - Subtítulo: Roboto Regular 16px na cor **PF-Grey300 (`#BDBEC3`)**.
  - Brasão da Polícia Federal: Inserido em alta definição à direita ou ao centro com área de respiro.
  - Botão de Ação Primária: Fundo **PF-Blue500 (`#3363CC`)** com texto branco, altura 40px ou 48px, rótulo direto (ex: "Iniciar Atendimento", "Solicitar Passaporte").

- **Opção B (Light Institucional - Alto Contraste)**:
  - Fundo: Branco (`#FFFFFF`) ou **PF-Grey100 (`#ECEDEE`)**.
  - Título (`h1`): Roboto Bold 36px na cor **PF-Grey700 (`#41434E`)**.
  - Filete inferior de destaque: Linha de 4px na cor **PF-Gold500 (`#E1AD62`)**.

### 3.3. Cards de Serviços (Grid de 8px)
Organizados em colunas responsivas utilizando o sistema PrimeFlex:
- Padding interno dos cards: `24px` ou `32px` (múltiplos de 8px).
- Borda: `1px solid #DADADD` (`PF-Grey200`), com raio de borda de `4px` ou `8px`.
- Hover sutil: Elevação suave com sombra leve e borda em **PF-Blue500 (`#3363CC`)**.
- Ícones: FontAwesome 5 Free (ex: `fas fa-passport`, `fas fa-fingerprint`, `fas fa-shield-alt`) na cor **PF-Blue500** ou **PF-Gold600**.

### 3.4. Etapas e Passo a Passo (Workflow)
Apresenta o fluxo que o cidadão percorrerá para obter o serviço:
1. Preenchimento do formulário eletrônico.
2. Pagamento da Guia de Recolhimento da União (GRU).
3. Agendamento presencial no posto da PF.
4. Comparecimento e entrega do documento.

Cada etapa deve conter um numeral em destaque circular com fundo **PF-Blue500** ou **PF-Gold500**.

### 3.5. Perguntas Frequentes (Accordion)
- Utilizar o componente Accordion estilizado no padrão Frontline.
- Títulos de dúvidas em Roboto Medium 16px.
- Respostas objetivas com links oficiais para orientações complementares.

### 3.6. Rodapé Oficial
- Informações de Copyright: `© Polícia Federal. Todos os direitos reservados.`
- Links institucionais: Acesso à Informação, Legislação Federal, Portal da Transparência, Ouvidoria da PF.
- Ícones para redes sociais oficiais (Instagram, Twitter, LinkedIn, YouTube) ativadas quando `showSocialNetworks: true`.

---

## 4. Código Template de Exemplo para Landing Page

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Polícia Federal — Emissão de Passaporte</title>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <style>
    :root {
      --pf-black: #111213;
      --pf-gold: #E1AD62;
      --pf-blue: #3363CC;
      --pf-blue-hover: #1F628D;
      --pf-grey-text: #41434E;
      --pf-grey-sub: #6A6D7C;
      --pf-bg-light: #F4F6F8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Roboto', sans-serif; color: var(--pf-grey-text); background: #FFF; line-height: 1.5; }
    
    /* Barra Gov.br */
    .gov-bar { background: #000; color: #FFF; padding: 8px 32px; font-size: 12px; display: flex; justify-content: space-between; }
    .gov-bar a { color: #FFF; text-decoration: none; margin-left: 16px; }

    /* Hero Section */
    .hero-section {
      background-color: var(--pf-black);
      color: #FFF;
      padding: 64px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 4px solid var(--pf-gold);
    }
    .hero-content { max-width: 640px; }
    .hero-badge { display: inline-block; background: rgba(225, 173, 98, 0.15); color: var(--pf-gold); padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 700; margin-bottom: 16px; border: 1px solid var(--pf-gold); }
    .hero-title { font-size: 36px; font-weight: 700; line-height: 1.2; margin-bottom: 16px; }
    .hero-subtitle { font-size: 16px; color: #BDBEC3; margin-bottom: 32px; }
    .btn-primary { background: var(--pf-blue); color: #FFF; padding: 12px 32px; font-size: 16px; font-weight: 500; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; transition: background 0.2s; }
    .btn-primary:hover { background: var(--pf-blue-hover); }

    /* Grid de Serviços */
    .services-container { max-width: 1200px; margin: 64px auto; padding: 0 24px; }
    .section-title { font-size: 28px; font-weight: 700; margin-bottom: 32px; text-align: center; }
    .services-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }
    .service-card { background: #FFF; border: 1px solid #DADADD; border-radius: 8px; padding: 32px 24px; transition: transform 0.2s, border-color 0.2s; }
    .service-card:hover { transform: translateY(-4px); border-color: var(--pf-blue); }
    .service-icon { font-size: 32px; color: var(--pf-blue); margin-bottom: 16px; }
    .service-title { font-size: 18px; font-weight: 700; margin-bottom: 8px; }
    .service-desc { font-size: 14px; color: var(--pf-grey-sub); }
  </style>
</head>
<body>
  <div class="gov-bar">
    <span>BRASIL — MINISTÉRIO DA JUSTIÇA E SEGURANÇA PÚBLICA</span>
    <div>
      <a href="#conteudo">Ir para o conteúdo [Alt+1]</a>
      <a href="#acessibilidade">Acessibilidade</a>
      <a href="#contraste">Alto Contraste</a>
    </div>
  </div>

  <section class="hero-section" id="conteudo">
    <div class="hero-content">
      <span class="hero-badge"><i class="fas fa-shield-alt"></i> SERVIÇO OFICIAL DA POLÍCIA FEDERAL</span>
      <h1 class="hero-title">Emissão e Renovação de Passaporte Brasileiro</h1>
      <p class="hero-subtitle">Realize a solicitação online, gere a Guia de Recolhimento da União (GRU) e agende seu atendimento presencial no posto mais próximo.</p>
      <a href="#" class="btn-primary">Iniciar Solicitação <i class="fas fa-arrow-right"></i></a>
    </div>
    <div class="hero-visual">
      <i class="fas fa-passport" style="font-size: 140px; color: var(--pf-gold); opacity: 0.9;"></i>
    </div>
  </section>

  <main class="services-container">
    <h2 class="section-title">Serviços Disponíveis</h2>
    <div class="services-grid">
      <div class="service-card">
        <i class="fas fa-file-invoice service-icon"></i>
        <h3 class="service-title">Solicitar Passaporte</h3>
        <p class="service-desc">Inicie o preenchimento do formulário com seus dados civis e biográficos.</p>
      </div>
      <div class="service-card">
        <i class="fas fa-barcode service-icon"></i>
        <h3 class="service-title">Reemissão de GRU</h3>
        <p class="service-desc">Gere a 2ª via da taxa de recolhimento para pagamento na rede bancária.</p>
      </div>
      <div class="service-card">
        <i class="fas fa-calendar-check service-icon"></i>
        <h3 class="service-title">Agendar Atendimento</h3>
        <p class="service-desc">Consulte datas e horários disponíveis nas delegacias e postos da PF.</p>
      </div>
      <div class="service-card">
        <i class="fas fa-search service-icon"></i>
        <h3 class="service-title">Consultar Andamento</h3>
        <p class="service-desc">Acompanhe a confecção e previsão de entrega do seu documento.</p>
      </div>
    </div>
  </main>
</body>
</html>
```
