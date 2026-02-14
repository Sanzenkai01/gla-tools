GLA Tools — versão web

Esta pasta contém a versão web (HTML/CSS/JS) reescrita da sua aplicação `GLA Tools`.

O que foi feito
- Reescrevi o aplicativo como uma single-page app estática (`index.html`, `styles.css`, `script.js`).
- Mantidas as 3 calculadoras: Experiência, Receitas e Cristais (mesma lógica que o `app.py`).
- Aproveitei as imagens já presentes em `assets/`.
- Adicionei um workflow GitHub Actions para publicar automaticamente no GitHub Pages quando você der push na branch `main`.

Como publicar no GitHub Pages
1. Faça commit e push deste repositório para o GitHub (branch `main`).
2. (Opcional) O workflow `pages.yml` fará o deploy automático após o push — verifique a aba Actions para confirmar.
3. Caso prefira publicar manualmente: vá em Settings → Pages → Source → selecione `main` / `/(root)` e salve.
4. A URL ficará em: `https://<seu-usuario>.github.io/<nome-do-repositorio>/` (pode demorar alguns minutos).

Observações
- Não removi nem modifiquei a lógica original em `app.py`; a nova versão web está em `index.html` (root) e usa os mesmos dados e algoritmos.
- Se quiser que eu publique para você (criar branch/PR, ajustar o domínio ou melhorar o design), diga qual passo deseja que eu execute a seguir.

---
Se quiser que eu converta a UI para outro framework (React/Vue) ou adicione CI/CD extra (ex.: deploy para Netlify/Render), posso fazer isto também.
