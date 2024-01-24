import { ReactNode } from "react"
import { Link } from "react-router-dom"
import Sidebar from "./Sidebar"
import Content from "./Content"


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
        { 
            emoji: '🎬',
            linkTo: '/settings',
            text: 'Configurer',
        },
    ]
    return (
        <div className="min-h-screen sm:min-h-auto flex flex-col sm:flex-row w-screen">
            <nav className="sm:h-screen sticky top-0 sm:w-1/6 bg-gray-200 text-justify pt-2">
                <ul>
                { entries.map(({ linkTo, text, emoji }) => (
                    <li className="pr-2 pl-2" key={ text }>
                        <Link className="w-full text-gray-900 bg-white focus:bg-gray-100 hover:bg-gray-100 border border-gray-200 focus:ring-gray-100 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center dark:focus:ring-gray-600 dark:bg-gray-800 dark:border-gray-700 dark:text-white dark:hover:bg-gray-700 me-2 mb-2" to={ linkTo }>
                        <span className="mr-2">{ emoji }</span>
                        <span>{ text }</span></Link>
                    </li>
                ) ) }
                </ul>
            </nav>
            <main className="sm:w-5/6 flex-grow flex-1 flex">
                { children }
            </main>
        </div>
    )
}