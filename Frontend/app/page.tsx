import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-black relative overflow-hidden">

      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex items-center justify-center px-4">
        <div className="text-center max-w-2xl mx-auto">
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 md:p-12 border border-white/20">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">CleanSight</h1>
            <p className="text-lg md:text-xl text-gray-300 mb-8 leading-relaxed">
              Welcome to CleanSight, a Data Quality & Anomaly Detection Tool — your smart assistant for ensuring clean, 
              reliable, and trustworthy data. Effortlessly upload your datasets, and let our platform automatically 
              analyze data quality, detect anomalies, and generate insightful reports. 
            </p>
            <p className="text-md text-gray-400 mb-10">
              Whether you’re a data analyst, scientist, or business user, this tool helps you identify issues, maintain data integrity, and make 
              better decisions with confidence. CleanSight automatically detects data inconsistencies, missing values,
              and outliers while generating detailed visualizations and recommendations for optimal data preprocessing.
            </p>
            <Link href="/app">
              <Button
                size="lg"
                className="bg-white text-black hover:bg-gray-200 text-lg px-8 py-3 rounded-full font-semibold transition-all duration-300 transform hover:scale-105"
              >
                Launch CleanSight
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
