import { Outlet, Link } from "react-router-dom"


export default function Root() {
    return (
        <>
            <aside className="fixed top-0 left-0 z-40 w-64 h-screen transition-transform -translate-x-full sm:translate-x-0" aria-label="Sidebar">
                <div className="h-full px-3 py-4 overflow-y-auto bg-gray-50 dark:bg-gray-800">
                    <ul className="space-y-2 font-medium">
                        <li><Link to={ `/camera` }><span className="ms-3">Appareil photo</span></Link></li>
                        <li><span className="ms-3">Gallerie</span></li>
                        <li><span className="ms-3">Photos</span></li>
                    </ul>
                </div>
            </aside>
            <div>
                <header className="sticky top-0 border-b mb-4 text-4xl font-extrabold leading-none tracking-tight text-gray-900 md:text-5xl lg:text-6xl dark:text-white">
                    <h1>Timelapse</h1>
                </header>
                <main className="p-4">
                    <Outlet />
                </main>  
            </div>
        </>
    )
}