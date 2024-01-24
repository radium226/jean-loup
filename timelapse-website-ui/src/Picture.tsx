
export interface PictureProps {
    source: string | null
}


export default function Picture({ source  }: PictureProps) {
    return (
        source !== null ? <img className="object-contain min-h-full w-auto rounded" src={source} /> : <div className="text-6xl"><div className="object-contain">🪴</div></div>
    )
}