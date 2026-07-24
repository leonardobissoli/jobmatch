import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Termos de Uso — Job Match",
  robots: { index: false, follow: false },
};

export default function TermsPage() {
  return (
    <main className="min-h-screen px-4 py-12 md:py-20">
      <article className="mx-auto max-w-[760px]">
        <Link href="/" className="text-fg-muted hover:text-fg-primary text-sm">
          ← Voltar
        </Link>
        <h1 className="text-3xl md:text-4xl font-bold mt-6 mb-6 text-fg-primary">
          Termos de Uso
        </h1>
        <div className="space-y-4 text-fg-muted leading-relaxed">
          <p>Versão local: 2026-07-24.</p>

          <h2 className="text-xl font-bold text-fg-primary mt-8">Uso permitido</h2>
          <ul className="list-disc list-inside space-y-1">
            <li>Submeter o seu próprio CV em PDF e a descrição de uma vaga em TXT.</li>
            <li>Receber uma análise de aderência informativa, sem garantia.</li>
          </ul>

          <h2 className="text-xl font-bold text-fg-primary mt-8">Uso proibido</h2>
          <ul className="list-disc list-inside space-y-1">
            <li>Submeter currículo de terceiros sem consentimento explícito.</li>
            <li>Tentar explorar a aplicação, o modelo selecionado ou os sistemas locais.</li>
            <li>Submeter conteúdo ilegal, ofensivo ou que viole direitos de terceiros.</li>
          </ul>

          <h2 className="text-xl font-bold text-fg-primary mt-8">Sem garantias</h2>
          <p>
            O relatório é gerado por modelo de linguagem e tem fins informativos. Pode conter
            imprecisões. O serviço é oferecido &quot;como está&quot;, sem garantia de
            disponibilidade, exatidão ou adequação a qualquer propósito.
          </p>

          <h2 className="text-xl font-bold text-fg-primary mt-8">Limitação de responsabilidade</h2>
          <p>
            Em nenhum caso o autor responderá por decisões tomadas com base no relatório.
            Recomenda-se conferir o resultado contra a descrição original da vaga e seu CV.
          </p>

          <h2 className="text-xl font-bold text-fg-primary mt-8">Privacidade</h2>
          <p>
            O tratamento de dados está descrito na{" "}
            <Link href="/privacy" className="underline hover:text-fg-primary">
              Política de Privacidade
            </Link>
            .
          </p>

          <h2 className="text-xl font-bold text-fg-primary mt-8">Contato</h2>
          <p>
            Envie um DM no LinkedIn para Leonardo Bissoli.
          </p>
        </div>
      </article>
    </main>
  );
}
