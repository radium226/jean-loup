import { ReactNode } from "react"
import { Link } from "react-router-dom"


export interface LayoutProps {
    children: ReactNode
}

interface Entry {
    emoji: string,
    linkTo: string,
    text: string,
} 

export default function Layout({ children }: LayoutProps) {
    const entries: Entry[] = [
        { 
            emoji: '📸',
            linkTo: '/camera',
            text: 'Prendre une photo',
        },
        { 
            emoji: '🎞️',
            linkTo: '/gallery',
            text: 'Parcourir la gallerie',
        },
        { 
            emoji: '🎬',
            linkTo: '/timelapse',
            text: 'Générer le timelapse',
        },
    ]
    return (
        <div>
            <header>

            </header>
            <nav>
            </nav>
            <section>
                { children }
            </section>
            <aside className="fixed top-0 left-0 z-40 w-64 h-screen">
                <div className="h-full py-4 px-4 bg-gray-100 text-left">
                    <ul>
                        { entries.map((entry) => (
                            <li className={ `hover:bg-gray-200 font-bold py-2 px-4 rounded py-4 before:content-['${entry.emoji}'] before:mx-1` }>
                                <Link className="py-2" to={ entry.linkTo }>{ entry.text }</Link>
                            </li>
                        )) }
                    </ul>
                </div>
            </aside>
            <footer>

            </footer>
        </div>
    )
}