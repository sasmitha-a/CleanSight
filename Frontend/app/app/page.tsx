"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Upload, FileText, BarChart3, Download, X } from "lucide-react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"

interface AnalysisReport {
  summary: string
  dataQuality: number
  missingValues: number
  outliers: number
  recommendations: string[]
  visualizations: string[]
}

export default function AppPage() {
  const [file, setFile] = useState<File | null>(null)
  const [textData, setTextData] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [report, setReport] = useState<AnalysisReport | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [reportId, setReportId] = useState<string | null>(null)

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setTextData("")
    }
  }

  const handleSubmit = async () => {
    if (!file && !textData.trim()) {
      alert("Please upload a file or enter dataset text")
      return
    }

    setIsLoading(true)

    try {
      const formData = new FormData()

      if (file) {
        formData.append("file", file)
      } else {
        formData.append("pasted_data", textData)
      }

      const response = await fetch("http://localhost:8000/analyze/", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("Analysis failed")
      }

      const result = await response.json()

      const actualReport: AnalysisReport = {
        summary: result.summary,
        dataQuality: result.data_quality,
        missingValues: result.missing_values,
        outliers: result.outliers,
        recommendations: result.recommendations,
        visualizations: [
          "Distribution plots for numerical columns",
          "Missing value heatmap",
          "Correlation matrix",
          "Outlier detection scatter plots",
        ],
      }

      setReportId(result.report_id)
      setReport(actualReport)
      setShowModal(true)
    } catch (error) {
      console.error("Error analyzing dataset:", error)
      alert("Failed to analyze dataset. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const downloadPDF = async () => {
    if (!reportId) {
      alert("No report available for download.")
      return
    }
    try {
      const response = await fetch(`http://localhost:8000/download-report/${reportId}`)
      if (!response.ok) {
        throw new Error("PDF download failed")
      }
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = "DataQualityReport.pdf"
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error("Error downloading PDF:", error)
      alert("Failed to download PDF. Please try again.")
    }
  }
  

  const downloadPreprocessed = async () => {
    console.log("Trying to download preprocessed for reportId:", reportId);
  if (!reportId) {
    alert("No preprocessed dataset available for download.")
    return
  }
  try {
    const response = await fetch(`http://localhost:8000/download-preprocessed/${reportId}`)
    if (!response.ok) {
      throw new Error("Preprocessed dataset download failed")
    }
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "PreprocessedDataset.csv"
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (error) {
    console.error("Error downloading preprocessed dataset:", error)
    alert("Failed to download preprocessed dataset. Please try again.")
  }
}

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold text-gray-900">CleanSight</h1>
            </div>
            <Button variant="outline" onClick={() => (window.location.href = "/")}>
              Back to Home
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Welcome to CleanSight</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Upload your dataset and let our AI-powered analysis engine provide comprehensive insights, data quality
            assessments, and actionable recommendations for optimal data preprocessing.
          </p>
        </div>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Upload className="h-5 w-5" />
              <span>Dataset Upload</span>
            </CardTitle>
            <CardDescription>Upload a CSV, Excel file, or paste your dataset directly</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="file-upload">Upload File</Label>
              <Input
                id="file-upload"
                type="file"
                accept=".csv,.xlsx,.xls,.json,.txt"
                onChange={handleFileUpload}
                className="cursor-pointer"
              />
              {file && (
                <p className="text-sm text-green-600 flex items-center space-x-1">
                  <FileText className="h-4 w-4" />
                  <span>Selected: {file.name}</span>
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="text-data">Or Paste Dataset Text</Label>
              <Textarea
                id="text-data"
                placeholder="Paste your CSV data or JSON data here..."
                value={textData}
                onChange={(e) => {
                  setTextData(e.target.value)
                  if (e.target.value.trim()) {
                    setFile(null)
                  }
                }}
                rows={6}
                className="font-mono text-sm"
              />
            </div>

            <Button
              onClick={handleSubmit}
              disabled={isLoading || (!file && !textData.trim())}
              className="w-full"
              size="lg"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Analyzing Dataset...
                </>
              ) : (
                <>
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Analyze Dataset
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>How CleanSight Works</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="bg-blue-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                  <Upload className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="font-semibold mb-2">1. Upload Data</h3>
                <p className="text-sm text-gray-600">Upload your dataset in various formats or paste text directly</p>
              </div>
              <div className="text-center">
                <div className="bg-green-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                  <BarChart3 className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="font-semibold mb-2">2. AI Analysis</h3>
                <p className="text-sm text-gray-600">Our AI engine analyzes data quality, patterns, and anomalies</p>
              </div>
              <div className="text-center">
                <div className="bg-purple-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                  <FileText className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="font-semibold mb-2">3. Get Report</h3>
                <p className="text-sm text-gray-600">Receive detailed insights and download comprehensive reports</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>

      <Dialog open={showModal} onOpenChange={setShowModal}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center justify-between">
              <span className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5" />
                <span>Data Analysis Report</span>
              </span>
              <Button variant="ghost" size="sm" onClick={() => setShowModal(false)}>
                <X className="h-4 w-4" />
              </Button>
            </DialogTitle>
          </DialogHeader>

          {report && (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Executive Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700">{report.summary}</p>
                </CardContent>
              </Card>

              <div className="grid md:grid-cols-3 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{report.dataQuality}%</div>
                      <p className="text-sm text-gray-600">Data Quality Score</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">{report.missingValues}</div>
                      <p className="text-sm text-gray-600">Missing Values</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">{report.outliers}</div>
                      <p className="text-sm text-gray-600">Outliers Detected</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Recommendations</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {report.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <div className="bg-blue-100 rounded-full w-6 h-6 flex items-center justify-center mt-0.5 flex-shrink-0">
                          <span className="text-xs font-semibold text-blue-600">{index + 1}</span>
                        </div>
                        <span className="text-gray-700">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <div className="flex justify-center space-x-4 pt-4">
                <Button onClick={downloadPDF} size="lg" className="px-8">
                  <Download className="h-4 w-4 mr-2" />
                  Download Full Report (PDF)
                </Button>
                <Button onClick={downloadPreprocessed} size="lg" className="px-8">
                  <Download className="h-4 w-4 mr-2" />
                  Download Preprocessed Data (CSV)
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
