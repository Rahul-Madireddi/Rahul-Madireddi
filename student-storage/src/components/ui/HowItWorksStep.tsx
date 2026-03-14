import type { LucideIcon } from 'lucide-react';

interface HowItWorksStepProps {
  step: number;
  icon: LucideIcon;
  title: string;
  description: string;
}

export default function HowItWorksStep({ step, icon: Icon, title, description }: HowItWorksStepProps) {
  return (
    <div className="flex flex-col items-center text-center gap-5">
      <div className="relative">
        <div className="w-16 h-16 bg-indigo-50 rounded-2xl flex items-center justify-center">
          <Icon size={28} className="text-indigo-600" />
        </div>
        <div className="absolute -top-2 -right-2 w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
          {step}
        </div>
      </div>
      <div>
        <h3 className="text-gray-900 font-semibold text-lg mb-2">{title}</h3>
        <p className="text-gray-500 text-sm leading-relaxed max-w-xs mx-auto">{description}</p>
      </div>
    </div>
  );
}
