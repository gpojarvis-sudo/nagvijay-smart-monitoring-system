import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '@/services/api'
import { Building2, Search, Plus, MapPin, Phone, Mail } from 'lucide-react'

export default function OfficeMasterPage() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['offices', page, search],
    queryFn: async () => {
      const res = await api.get(`/offices?page=${page}&page_size=20&search=${search}`)
      return res.data
    }
  })

  const offices = data?.data || [
    { id: '1', office_code: 'NG-HO-001', office_name: 'Nagpur Head Office', office_type: 'HEAD_OFFICE', division: 'Nagpur City', pincode: '440001', district: 'Nagpur', status: 'ACTIVE', total_employees: 45 },
    { id: '2', office_code: 'NG-SO-012', office_name: 'Sitabuldi SO', office_type: 'SUB_OFFICE', division: 'Nagpur City', pincode: '440012', district: 'Nagpur', status: 'ACTIVE', total_employees: 12 },
    { id: '3', office_code: 'NG-BO-045', office_name: 'Itwari BO', office_type: 'BRANCH_OFFICE', division: 'Nagpur City', pincode: '440002', district: 'Nagpur', status: 'ACTIVE', total_employees: 3 },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3"><Building2 className="text-red-600" /> Office Master</h1>
          <p className="text-gray-600 mt-1">Manage HO, SO, BO hierarchy for Nagpur City Division</p>
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2.5 bg-red-600 text-white rounded-xl hover:bg-red-700 font-medium">
          <Plus size={18} /> Add Office
        </button>
      </div>

      <div className="bg-white rounded-xl border shadow-sm">
        <div className="p-6 border-b">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by office name, code, pincode..."
                className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent"
              />
            </div>
            <select className="px-4 py-2.5 border border-gray-300 rounded-xl">
              <option>All Types</option>
              <option>HEAD_OFFICE</option>
              <option>SUB_OFFICE</option>
              <option>BRANCH_OFFICE</option>
            </select>
            <select className="px-4 py-2.5 border border-gray-300 rounded-xl">
              <option>Nagpur City Division</option>
            </select>
          </div>
        </div>

        <div className="p-6">
          {isLoading ? (
            <div className="space-y-3 animate-pulse">
              {[1,2,3].map(i => <div key={i} className="h-20 bg-gray-100 rounded-xl"></div>)}
            </div>
          ) : (
            <div className="grid gap-4">
              {offices.map((office: any) => (
                <div key={office.id} className="border rounded-xl p-5 hover:shadow-md transition-shadow card-hover">
                  <div className="flex items-start justify-between">
                    <div className="flex gap-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-orange-500 rounded-xl flex items-center justify-center text-white font-bold">
                        {office.office_code.slice(0,2)}
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{office.office_name}</h3>
                        <p className="text-sm text-gray-600 flex items-center gap-2 mt-1">
                          <span className="px-2 py-0.5 bg-gray-100 rounded-full text-xs font-medium">{office.office_code}</span>
                          <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full text-xs">{office.office_type}</span>
                          <span className="px-2 py-0.5 bg-green-50 text-green-700 rounded-full text-xs">{office.status}</span>
                        </p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                          <span className="flex items-center gap-1"><MapPin size={12} /> {office.district} • {office.pincode} • {office.division}</span>
                          <span className="flex items-center gap-1"><Phone size={12} /> {office.total_employees} employees</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button className="px-3 py-1.5 border rounded-lg text-xs hover:bg-gray-50">View</button>
                      <button className="px-3 py-1.5 bg-red-50 text-red-700 border border-red-200 rounded-lg text-xs hover:bg-red-100">Edit</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-6 border-t flex items-center justify-between">
          <p className="text-sm text-gray-500">Showing {offices.length} offices • Total 150 in Nagpur City</p>
          <div className="flex gap-2">
            <button onClick={() => setPage(Math.max(1, page-1))} className="px-3 py-1.5 border rounded-lg text-sm">Prev</button>
            <span className="px-3 py-1.5 bg-red-600 text-white rounded-lg text-sm">{page}</span>
            <button onClick={() => setPage(page+1)} className="px-3 py-1.5 border rounded-lg text-sm">Next</button>
          </div>
        </div>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
        <h4 className="font-medium text-amber-900 text-sm">Google Sheets & Forms Integration</h4>
        <p className="text-xs text-amber-800 mt-1">Bulk import via Google Sheets: Set GOOGLE_SHEETS_CREDENTIALS_JSON. Field collection via Google Forms webhook at /api/v1/integrations/forms/webhook with X-Webhook-Secret header.</p>
      </div>
    </div>
  )
}
