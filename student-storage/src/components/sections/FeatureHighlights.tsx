import { Thermometer, Lock, MapPin, Clock, Smartphone, HeartHandshake } from 'lucide-react';

const features = [
  {
    icon: Thermometer,
    title: 'Climate Controlled',
    description: 'Your belongings stay safe year-round in our temperature-regulated storage facility.',
  },
  {
    icon: Lock,
    title: 'Secure & Insured',
    description: 'Every unit is monitored 24/7. All items are covered by our comprehensive storage insurance.',
  },
  {
    icon: MapPin,
    title: 'Campus Pickup',
    description: 'We come directly to your dorm or apartment. No need to haul anything across campus.',
  },
  {
    icon: Clock,
    title: 'Flexible Dates',
    description: 'Choose your pickup and delivery windows. We work around your finals and move-out schedule.',
  },
  {
    icon: Smartphone,
    title: 'Online Inventory',
    description: 'Track every item you store through our online dashboard. Know exactly what you have stored.',
  },
  {
    icon: HeartHandshake,
    title: 'Student-First Service',
    description: 'Built for students, priced for students. Our team understands the chaos of semester transitions.',
  },
];

export default function FeatureHighlights() {
  return (
    <section className="py-24 bg-white">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-16">
          <p className="text-indigo-600 font-semibold text-sm uppercase tracking-widest mb-3">
            Why StoreSafe
          </p>
          <h2 className="text-4xl font-bold text-gray-950 tracking-tight">
            Everything you need, nothing you don't
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map(({ icon: Icon, title, description }) => (
            <div
              key={title}
              className="p-7 rounded-3xl border border-gray-100 hover:border-indigo-100 hover:bg-indigo-50/30 transition-all duration-300 group"
            >
              <div className="w-12 h-12 bg-indigo-50 rounded-2xl flex items-center justify-center mb-5 group-hover:bg-indigo-100 transition-colors">
                <Icon size={22} className="text-indigo-600" />
              </div>
              <h3 className="text-gray-900 font-semibold mb-2">{title}</h3>
              <p className="text-gray-500 text-sm leading-relaxed">{description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
