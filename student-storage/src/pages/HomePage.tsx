import Hero from '../components/sections/Hero';
import HowItWorks from '../components/sections/HowItWorks';
import FeatureHighlights from '../components/sections/FeatureHighlights';
import PricingPreview from '../components/sections/PricingPreview';
import Testimonials from '../components/sections/Testimonials';
import FAQSection from '../components/sections/FAQSection';
import CTABanner from '../components/sections/CTABanner';

export default function HomePage() {
  return (
    <>
      <Hero />
      <HowItWorks />
      <FeatureHighlights />
      <PricingPreview />
      <Testimonials />
      <FAQSection />
      <CTABanner />
    </>
  );
}
