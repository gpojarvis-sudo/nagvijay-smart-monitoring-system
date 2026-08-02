from pathlib import Path

content = r'''import { useEffect, useState } from "react";
import api from "@/services/api";

export default function DailyMonitoringPage() {
  const today = new Date().toISOString().split("T")[0];

  const [loading, setLoading] = useState(false);
  const [offices, setOffices] = useState([]);

  const [form, setForm] = useState({
    report_date: today,
    office_code: "",
    sb_opened: "",
    sb_closed: "",
    net_accounts: "",
    pli_policies: "",
    sum_assured: "",
    premium: "",
    speed_post_document: "",
    speed_post_parcel: "",
    business_post: "",
    logistics: "",
    international_letter: "",
    aadhaar_transactions: "",
    aadhaar_amount: "",
    ippb_transactions: "",
    ippb_amount: ""
  });

  useEffect(() => {
    loadOffices();
  }, []);

  async function loadOffices() {
    try {
      setLoading(true);
      const res = await api.get("/offices?page_size=100");
      setOffices(res.data.data || []);
    } catch (e) {
      console.error(e);
      alert("Unable to load offices");
    } finally {
      setLoading(false);
    }
  }

  function update(e) {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  }

  async function submit(e) {
    e.preventDefault();

    try {
      await api.post("/daily-reports", form);
      alert("Report submitted successfully.");
    } catch (err) {
      console.error(err);
      alert("Submission failed.");
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Daily Monitoring Report</h1>

      <form onSubmit={submit} className="space-y-6">

        <div className="grid grid-cols-2 gap-4">

          <input
            type="date"
            name="report_date"
            value={form.report_date}
            onChange={update}
            className="border rounded-lg p-3"
          />

          <select
            name="office_code"
            value={form.office_code}
            onChange={update}
            className="border rounded-lg p-3"
          >
            <option value="">
              {loading ? "Loading Offices..." : "Select Office"}
            </option>

            {offices.map((o) => (
              <option key={o.id} value={o.office_code}>
                {o.office_name}
              </option>
            ))}

          </select>

        </div>

      </form>

    </div>
  );
}
'''

Path("src/pages/DailyMonitoringPage.tsx").write_text(content)
print("DailyMonitoringPage.tsx generated successfully.")
