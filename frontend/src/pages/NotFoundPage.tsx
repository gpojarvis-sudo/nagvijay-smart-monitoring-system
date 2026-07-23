import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-900">404</h1>
        <p className="mt-4 text-xl text-gray-600">Page not found</p>
        <p className="mt-2 text-sm text-gray-500">The page you're looking for doesn't exist in NagVijay NSMS</p>
        <Link to="/dashboard" className="mt-6 inline-flex px-6 py-3 bg-red-600 text-white rounded-xl hover:bg-red-700">Go to Dashboard</Link>
      </div>
    </div>
  )
}
