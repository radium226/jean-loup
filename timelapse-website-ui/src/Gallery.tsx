import { Client, Picture } from "./client"
import { useState, useEffect, useCallback } from 'react'
import { toDataURL } from "./utils"

export interface GalleryProps {
    client: Client
}


export interface FrameProps {
    picture: Picture,
    downloadPictureThumbnail: (picture: Picture) => Promise<Blob>,
}

export function Frame({ picture, downloadPictureThumbnail }: FrameProps) {
    const [source, setSource] = useState<string | null>(null)

    const downloadThumbnail = useCallback(async () => {
        const blob = await downloadPictureThumbnail(picture)
        const dataURL = await toDataURL(blob)
        setSource(dataURL)
    }, [picture])

    useEffect(() => {
        downloadThumbnail()
    }, [downloadThumbnail])

    return (
        <div className="h-auto max-w-full">
            <div>
                { source !== null ? <img className="rounded-lg" src={source} /> : <div className="text-6xl">🪴</div> }
            </div>
            <p>{ picture.id }</p>
        </div>
    )

}

export default function Gallery({ client }: GalleryProps) {
    
    const [pictures, setPictures] = useState<Picture[]>([])

    const listPictures = useCallback(async () => {
        const pictures = await client.listPictures()
        setPictures(pictures)
    }, [pictures])

    useEffect(() => {
        listPictures()
    }, [])

    return (
        <div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                { pictures.map((picture) => (
                    <Frame key={ picture.id } picture={ picture } downloadPictureThumbnail={ async (picture) => { return await client.downloadPictureThumbnail(picture) } } />
                ) ) }
            </div>
        </div>
    )
}