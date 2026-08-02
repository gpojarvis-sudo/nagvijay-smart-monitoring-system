import { FileText, Download } from 'lucide-react'
import { useState } from 'react'
import api from '@/services/api'

export default function ReportsPage() {
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState<any>(null)
  const [exporting, setExporting] = useState<string | null>(null)
  const [reportType, setReportType] = useState<string>('DAILY')

  const generate = async (type: string) => {
    setLoading(true)
    setReportType(type)
    try {
      const res = await api.post('/reports/generate', {
        report_type: type,
        filters: { division: 'Nagpur City', financial_year: '2024-25' },
        format: 'JSON'
      })
      setReport(res.data.data)
    } catch (e: any) {
      setReport({ error: e.message, sample: 'DPR sample - configure backend' })
    } finally {
      setLoading(false)
    }
  }

  const exportFile = async (format: 'PDF' | 'EXCEL' | 'CSV') => {
    setExporting(format)
    try {
      const res = await api.get('/reports/export', {
        params: {
          report_type: reportType,
          format,
          financial_year: '2024-25',
          division: 'Nagpur City',
        },
        responseType: 'blob',
      })
      const extension = format === 'EXCEL' ? 'xlsx' : format.toLowerCase()
      const blobUrl = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = `${reportType.toLowerCase()}_report.${extension}`
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(blobUrl)
    } catch (e: any) {
      alert('Export failed. Please try again.')
    } finally {
      setExporting(null)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold flex items-center gap-3"><FileText className="text-orange-600" /> Reports</h1>

      <div className="grid md:grid-cols-3 gap-4">
        {[
          { id: 'DAILY', name: 'Daily Performance Report', desc: 'DPR for today' },
          { id: 'MONTHLY', name: 'Monthly Consolidated', desc: 'Monthly report' },
          { id: 'OFFICE_WISE', name: 'Office-wise Report', desc: 'All offices performance' },
        ].map(r => (
          <div key={r.id} className="bg-white border rounded-xl p-5 hover:shadow-md">
            <h3 className="font-semibold">{r.name}</h3>
            <p className="text-sm text-gray-500 mt-1">{r.desc}</p>
            <button onClick={() => generate(r.id)} disabled={loading} className="mt-4 w-full py-2 bg-orange-600 text-white rounded-lg text-sm flex items-center justify-center gap-2">
              <FileText size={14} /> {loading ? 'Generating...' : 'Generate'}
            </button>
          </div>
        ))}
      </div>

      {report && (
        <div className="bg-white border rounded-xl p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold">Generated Report</h3>
            <div className="flex gap-2">
              <button
                onClick={() => exportFile('PDF')}
                disabled={exporting !== null}
                className="px-3 py-1.5 border rounded-lg text-sm flex items-center gap-2 disabled:opacity-50"
              >
                <Download size={14} /> {exporting === 'PDF' ? 'Exporting...' : 'Export PDF'}
              </button>
              <button
                onClick={() => exportFile('EXCEL')}
                disabled={exporting !== null}
                className="px-3 py-1.5 border rounded-lg text-sm flex items-center gap-2 disabled:opacity-50"
              >
                <Download size={14} /> {exporting === 'EXCEL' ? 'Exporting...' : 'Export Excel'}
              </button>
              <button
                onClick={() => exportFile('CSV')}
                disabled={exporting !== null}
                className="px-3 py-1.5 border rounded-lg text-sm flex items-center gap-2 disabled:opacity-50"
              >
                <Download size={14} /> {exporting === 'CSV' ? 'Exporting...' : 'Export CSV'}
              </button>
            </div>
          </div>
          <pre className="bg-gray-50 p-4 rounded-lg text-xs overflow-auto max-h-[400px]">{JSON.stringify(report, null, 2)}</pre>
        </div>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
        <p className="text-sm text-blue-800"><strong>n8n Automation:</strong> Scheduled reports via n8n webhook at /api/v1/integrations/n8n/trigger. Configure N8N_WEBHOOK_URL and enable N8N_ENABLED.</p>
      </div>
    </div>
  )
}
