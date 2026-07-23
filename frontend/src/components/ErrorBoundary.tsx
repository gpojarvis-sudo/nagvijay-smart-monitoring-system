import { Component, ReactNode } from 'react'

interface Props { children: ReactNode }
interface State { hasError: boolean; error?: Error }

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }
  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center p-6 bg-gray-50">
          <div className="bg-white border border-red-200 rounded-xl p-8 max-w-md">
            <h2 className="font-bold text-red-700">Something went wrong</h2>
            <p className="text-sm text-gray-600 mt-2">{this.state.error?.message}</p>
            <button onClick={() => window.location.reload()} className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg text-sm">Reload</button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
