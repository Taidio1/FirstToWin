import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/Button';

export default function NotFound() {
  return (
    <div className="flex min-h-[70vh] items-center justify-center">
      <div className="text-center">
        <div className="text-[6rem] font-bold leading-none text-accent">404</div>
        <h1 className="mt-2 text-xl font-semibold text-slate-100">Page not found</h1>
        <p className="mt-2 text-sm text-slate-400">
          The route you tried to reach doesn't exist in this console.
        </p>
        <Link to="/" className="inline-block">
          <Button className="mt-5">Back to dashboard</Button>
        </Link>
      </div>
    </div>
  );
}
