import './App.css'

import { Client } from './client'
import Camera from './Camera'
  

function App() {
  const client = new Client()
  return (
    <div>
      <header className="sticky top-0 border-b mb-4 text-4xl font-extrabold leading-none tracking-tight text-gray-900 md:text-5xl lg:text-6xl dark:text-white">
        <h1>Timelapse</h1>
      </header>
      <main className="p-4">
        <Camera client={ client } />
      </main>  
    </div>
  )
}

export default App
