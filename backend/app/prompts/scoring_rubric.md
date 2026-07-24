# Scoring Rubric — Job Match

Critérios para pontuar cada uma das 6 dimensões do Job Match Score. Cada
dimensão pontua de 0 a 100 de forma independente; o score final é a média
ponderada pelos pesos abaixo.

> Esta é a rubrica de referência da edição local. Ela produz scores
> consistentes e defensáveis, mas é deliberadamente mais simples que a
> calibração fina usada na edição hospedada. Ajuste os critérios ao seu
> contexto: a rubrica é um arquivo de texto, e o motor recarrega o que
> estiver aqui.

---

## 1. Hard Skills (Stack Técnico) — Peso 30%

Separar as skills da vaga em **must-have** e **nice-to-have**, listar as skills
do CV (declaradas e evidenciadas pela experiência) e calcular cobertura.

- Cobertura total dos must-have, com boa parte dos nice-to-have → 85-100.
- Cobertura total dos must-have, poucos nice-to-have → 70-84.
- Maioria dos must-have coberta → 50-69.
- Metade ou menos dos must-have → 25-49.
- Cobertura marginal dos must-have → 0-24.

Regras de comparação:

- Não punir divergência de versão que não bloqueia o trabalho ("Python 3.11"
  na vaga vs "Python" no CV é match).
- Divergência de profundidade é gap parcial: a vaga pede senioridade na skill
  e o CV mostra uso raso → contar metade do peso daquela skill.
- Skill declarada sem nenhuma evidência (sem experiência que a use, sem
  certificação, sem projeto) vale metade e deve ser sinalizada no relatório
  como declarada sem evidência.

## 2. Experiência Profissional — Peso 25%

Quatro subcomponentes, cada um de 0 a 100:

| Subcomponente              | Peso |
|----------------------------|------|
| Anos totais de experiência | 30%  |
| Anos no role/área da vaga  | 35%  |
| Match de indústria/setor   | 15%  |
| Senioridade                | 20%  |

- **Anos**: CV igual ou acima do exigido → 100. Cada ano de déficit reduz o
  score de forma acentuada; 3 anos abaixo já é aproximadamente metade.
- **Anos no role específico**: contar apenas o tempo no papel que a vaga pede,
  não o total de carreira. 8 anos de Backend + 1 de Data Engineer, para uma
  vaga de Data Engineer, conta 1 ano.
- **Indústria**: mesma indústria → 100; adjacente → ~75; diferente mas
  tech-heavy → ~50; muito distante → ~25. Se a vaga não trata indústria como
  requisito, dar 100.
- **Senioridade**: CV no nível da vaga ou acima → 100; um nível abaixo → ~70;
  dois níveis → ~40; três ou mais → ~10. Candidato acima do nível da vaga
  pontua ~80 (risco de expectativa desalinhada).

## 3. Educação & Certificações — Peso 15%

Metade do peso para formação acadêmica, metade para certificações.

- **Formação**: CV atende ou supera o nível exigido → 100. Um nível abaixo do
  exigido reduz proporcionalmente. Se a vaga aceita "formação **ou experiência
  equivalente**" e o CV tem experiência sólida no role, dar 100.
- **Certificações**: pontuar pela fração das certificações exigidas ou
  preferidas que o CV possui. Se a vaga não exige nenhuma, dar 100.

## 4. Idiomas — Peso 10%

Para cada idioma exigido, comparar o nível do CV com o nível mínimo pedido,
usando a escala Basic (A1-A2) / Intermediate (B1-B2) / Advanced (C1) /
Fluent (C2) / Native.

- CV no nível exigido ou acima → 100.
- Um nível abaixo → ~60; dois → ~30; três ou mais → ~10.
- Idioma exigido ausente do CV → 0.

Score da dimensão = média dos idiomas exigidos. Se a vaga não exige idioma
algum, dar 100.

Quando o CV não declara o nível, é aceitável inferir a partir de evidência
concreta (anos em ambiente de trabalho naquele idioma, formação no exterior,
publicações ou palestras). Toda inferência precisa ser marcada como tal no
relatório.

## 5. Soft Skills & Cultural Fit — Peso 10%

Soft skills raramente são verificáveis diretamente. Avaliar por sinais
observáveis no CV, partindo de um score base de 50 e ajustando:

- Somam: liderança técnica, mentoria, ensino ou palestras; histórico no
  método de trabalho que a vaga descreve; experiência multicultural;
  atividade pública (blog, open source, comunidade); evidência concreta dos
  valores que a vaga declara.
- Subtraem: sinais que contradizem o que a vaga pede (trocas muito frequentes
  quando a vaga pede estabilidade, ou perfil estático quando a vaga pede
  ambiente dinâmico).

Limitar o resultado a 0-100. Nunca inferir traço de personalidade sem um
sinal concreto no CV.

## 6. Localização & Logística — Peso 10%

| Item                       | Peso |
|----------------------------|------|
| Compatibilidade geográfica | 50%  |
| Modalidade (remote/hybrid) | 30%  |
| Autorização para trabalhar | 20%  |

- **Geografia**: mesma localidade, ou vaga remote-first → 100. Mesmo país com
  relocação prevista → alto. País diferente sem apoio à mudança → baixo.
- **Modalidade**: compatível → 100; incompatível (vaga presencial, candidato
  remote-only, ou vice-versa) → baixo. Se a preferência do candidato não
  aparece no CV, dar 100 e marcar como suposição.
- **Autorização**: candidato já autorizado a trabalhar no país da vaga, ou
  questão não aplicável → 100. Vaga que oferece patrocínio → alto. Vaga que
  não oferece e candidato precisa → 0. Se o CV não deixa claro, tratar como
  não informado, não como impedimento.

---

## Cálculo Final

```
Job Match Score = round(
    Hard Skills      * 0.30 +
    Experiência      * 0.25 +
    Educação         * 0.15 +
    Idiomas          * 0.10 +
    Soft Skills      * 0.10 +
    Localização      * 0.10
)
```

Resultado é um inteiro 0-100. Mapear para tier:

- 85-100 → 🟢 Strong Match
- 70-84  → 🟢 Good Match
- 55-69  → 🟡 Moderate Match
- 40-54  → 🟡 Stretch Match
- 0-39   → 🔴 Low Match

---

## Regras Anti-Inflação

1. **Nunca** dar 100 numa dimensão sem evidência explícita no CV.
2. Na dúvida entre dois tiers, escolher sempre o **menor**.
3. Skill declarada sem evidência vale **metade** do peso.
4. Anos de experiência contam **roles full-time**. Estágios e freelances valem
   metade, a menos que somem 12+ meses contínuos.
5. Não inferir skill por proximidade (saber SQL não implica saber Snowflake).
