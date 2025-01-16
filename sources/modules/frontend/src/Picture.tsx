
export interface PictureProps {
    source: string | null
}


export default function Picture({ source  }: PictureProps) {
    return (
        source !== null ? <img className="object-contain h-auto w-auto rounded-lg" src={source} /> : <div className="text-6xl"><div className="object-contain">🪴</div></div>
    )
}