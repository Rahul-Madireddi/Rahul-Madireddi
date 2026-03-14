import { Link } from 'react-router-dom';
import { Package, Mail, Phone, MapPin } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-gray-950 text-gray-400">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          {/* Brand */}
          <div>
            <Link to="/" className="flex items-center gap-2 text-white font-semibold text-lg mb-4">
              <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center">
                <Package size={16} className="text-white" />
              </div>
              StoreSafe
            </Link>
            <p className="text-sm leading-relaxed">
              Hassle-free storage solutions built for college students. Store smart, study hard,
              come back ready.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-white font-medium mb-4">Quick Links</h4>
            <ul className="space-y-3 text-sm">
              {[
                { to: '/', label: 'Home' },
                { to: '/services', label: 'Services & Pricing' },
                { to: '/book', label: 'Book Storage' },
                { to: '/contact', label: 'Contact Us' },
              ].map(({ to, label }) => (
                <li key={to}>
                  <Link to={to} className="hover:text-white transition-colors">
                    {label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-white font-medium mb-4">Get in Touch</h4>
            <ul className="space-y-3 text-sm">
              <li className="flex items-center gap-3">
                <Phone size={15} className="text-indigo-400 shrink-0" />
                (217) 555-0198
              </li>
              <li className="flex items-center gap-3">
                <Mail size={15} className="text-indigo-400 shrink-0" />
                hello@storesafe.com
              </li>
              <li className="flex items-start gap-3">
                <MapPin size={15} className="text-indigo-400 shrink-0 mt-0.5" />
                601 E John St, Champaign, IL 61820
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs">
          <p>© {new Date().getFullYear()} StoreSafe. All rights reserved.</p>
          <p>Made with ❤️ for college students everywhere.</p>
        </div>
      </div>
    </footer>
  );
}
