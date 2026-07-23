import { Users, Search, Plus } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import api from '@/services/api'
import { useState } from 'react'

export default function EmployeeMasterPage() {
  const [search, setSearch] = useState('')
  
  const { data } = useQuery({
    queryKey: ['employees', search],
    queryFn: async () => {
      const res = await api.get(`/employees?search=${search}`).catch(() => ({ data: { data: [] } }))
      return res.data
    }
  })

  const employees = data?.data || [
    { id: '1', employee_code: 'EMP-NG-001', full_name: 'Rajesh Kumar', designation: 'SPM', office_id: 'NG-SO-012', status: 'ACTIVE', category: 'GENERAL' },
    { id: '2', employee_code: 'EMP-NG-002', full_name: 'Priya Sharma', designation: 'PA', office_id: 'NG-HO-001', status: 'ACTIVE', category: 'OBC' },
    { id: '3', employee_code: 'EMP-NG-003', full_name: 'Amit Patel', designation: 'BPM', office_id: 'NG-BO-045', status: 'ACTIVE', category: 'GENERAL' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3"><Users className="text-blue-600" /> Employee Master</h1>
          <p className="text-gray-600 mt-1">Manage postal staff, GDS, hierarchy for Nagpur City</p>
        </div>
        <button className="h-fit px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 flex items-center gap-2 font-medium"><Plus size={18} /> Add Employee</button>
      </div>

      <div className="bg-white rounded-xl border shadow-sm p-6">
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search employee name, code, designation..." className="w-full pl-10 pr-4 py-2.5 border rounded-xl focus:ring-2 focus:ring-blue-500" />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-xs text-gray-500 border-b">
                <th className="pb-3 font-medium">Employee</th>
                <th className="pb-3 font-medium">Code</th>
                <th className="pb-3 font-medium">Designation</th>
                <th className="pb-3 font-medium">Office</th>
                <th className="pb-3 font-medium">Status</th>
                <th className="pb-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {employees.map((emp: any) => (
                <tr key={emp.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 bg-blue-100 rounded-full flex items-center justify-center text-blue-700 font-semibold text-sm">{emp.full_name.split(' ').map((n:string)=>n[0]).join('').slice(0,2)}</div>
                      <div>
                        <p className="font-medium text-sm">{emp.full_name}</p>
                        <p className="text-xs text-gray-500">{emp.category}</p>
                      </div>
                    </div>
                  </td>
                  <td className="py-4 text-sm font-mono">{emp.employee_code}</td>
                  <td className="py-4"><span className="px-2 py-1 bg-purple-50 text-purple-700 rounded-full text-xs border">{emp.designation}</span></td>
                  <td className="py-4 text-sm">{emp.office_id}</td>
                  <td className="py-4"><span className="px-2 py-1 bg-green-50 text-green-700 rounded-full text-xs border">{emp.status}</span></td>
                  <td className="py-4 flex gap-2">
                    <button className="px-3 py-1 border rounded-lg text-xs">View</button>
                    <button className="px-3 py-1 bg-blue-50 text-blue-700 border rounded-lg text-xs">Edit</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
