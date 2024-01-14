import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import './App.css'


function toBase64(blob: Blob): Promise<string> {
  return new Promise((onSuccess, onError) => {
    try {
      const reader = new FileReader()
      reader.onload = () => {
        const base64 = reader.result as string
        onSuccess(base64)
      }
      reader.readAsDataURL(blob)
    } catch(e) {
      onError(e);
    }
  })
}
  

function App() {


  const [takingPicture, setTakingPicture] = useState(false)
  const [imageSource, setImageSource] = useState<string>(reactLogo)

  useEffect(() => {
    if (takingPicture) {
      const invoke = async () => {
        console.log("Taking picuture... ")
        const response = await fetch("/api/pictures", {
          method: "POST",
        })
        const blob = await response.blob()
        const base64 = await toBase64(blob)
        const imageSource = `${base64}`
        console.log(imageSource)
        setImageSource(imageSource)
        setTakingPicture(false)
      }
      invoke().catch(console.error)
    }
  }, [takingPicture])

  return (
    <>
      <img height={800} width={600} src={imageSource} />
      <button onClick={ () => setTakingPicture(true) }>📷 Prendre une photo ! </button>
    </>
  )
}

export default App
