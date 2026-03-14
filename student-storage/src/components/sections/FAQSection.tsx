import FAQAccordion from '../ui/FAQAccordion';
import { faqs } from '../../data/faqs';

export default function FAQSection() {
  return (
    <section className="py-24 bg-gray-50">
      <div className="max-w-2xl mx-auto px-6">
        <div className="text-center mb-12">
          <p className="text-indigo-600 font-semibold text-sm uppercase tracking-widest mb-3">
            FAQ
          </p>
          <h2 className="text-4xl font-bold text-gray-950 tracking-tight">
            Answers to common questions
          </h2>
        </div>
        <FAQAccordion faqs={faqs} />
      </div>
    </section>
  );
}
