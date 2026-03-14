import { CalendarCheck, Truck, ArchiveRestore } from 'lucide-react';
import HowItWorksStep from '../ui/HowItWorksStep';

const steps = [
  {
    icon: CalendarCheck,
    title: 'Book Online',
    description:
      'Choose your storage plan, select pickup and delivery dates, and enter your dorm address — all in under 3 minutes.',
  },
  {
    icon: Truck,
    title: 'We Pick Up',
    description:
      'Our crew arrives at your scheduled time, loads everything up, and transports it to our secure, climate-controlled facility.',
  },
  {
    icon: ArchiveRestore,
    title: 'We Deliver Back',
    description:
      "When classes resume, we bring everything straight to your new dorm or apartment. You don't lift a finger.",
  },
];

export default function HowItWorks() {
  return (
    <section className="py-24 bg-gray-50">
      <div className="max-w-5xl mx-auto px-6">
        <div className="text-center mb-16">
          <p className="text-indigo-600 font-semibold text-sm uppercase tracking-widest mb-3">
            How It Works
          </p>
          <h2 className="text-4xl font-bold text-gray-950 tracking-tight">
            Three steps to stress-free storage
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 relative">
          {/* Connector line (desktop only) */}
          <div className="hidden md:block absolute top-8 left-1/3 right-1/3 h-px bg-indigo-100" />

          {steps.map((step, i) => (
            <HowItWorksStep key={step.title} step={i + 1} {...step} />
          ))}
        </div>
      </div>
    </section>
  );
}
