import { useState } from 'react'
import './App.css'

import { Client } from "./client"
import { toDataURL } from './utils'

import Spinner from './Spinner'
import Picture from './Picture'

export interface CameraProps {
    client: Client
}




function Camera ({ client }: CameraProps) {
    const [isTakingPicture, setIsTakingPicture] = useState(false)
    const [pictureSource, setPictureSource] = useState<string | null>(null)

    async function takePicture() {
        setIsTakingPicture(true)
        const picture = await client.takePicture()
        const blob = await client.downloadPictureContent(picture)
        const dataURL = await toDataURL(blob)
        setPictureSource(dataURL)
        setIsTakingPicture(false)
    }

    return (
        <div>
            <div className="container bg-gray-100 flex h-96 w-144 items-center justify-center">
            { isTakingPicture ? ( <Spinner /> ) : ( <Picture source={ pictureSource } /> ) }
            </div>
            <div>
                <button className="m-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onClick={ takePicture }>📷 Prendre une photo ! </button>
            </div>
        </div>
    )
}

export default Camera