import { useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function CSVImport() {
  const { token } = useAuth()
  const [importType, setImportType] = useState('sellers')
  const [file, setFile] = useState(null)
  const [job, setJob] = useState(null)

  async function upload() {
    const form = new FormData()
    form.append('import_type', importType)
    form.append('file', file)
    const created = await apiRequest('/imports/upload', { method: 'POST', token, body: form, isForm: true })
    const status = await apiRequest(`/imports/${created.job_id}`, { token })
    setJob(status)
  }

  return (
    <div>
      <h3>CSV Import</h3>
      <select value={importType} onChange={(e) => setImportType(e.target.value)}>
        <option value="sellers">sellers</option>
        <option value="inventory">inventory</option>
      </select>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={upload} disabled={!file}>Upload</button>
      {job && <pre>{JSON.stringify(job, null, 2)}</pre>}
    </div>
  )
}
