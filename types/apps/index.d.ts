/**
 * Use this file to add type declarations shared by your React apps and packages.
 */
declare module "*.md" {
    const md: string;
    export default md;
}

declare module "*.png" {
    const png: string;
    export default png;
}

declare module "*.jpg" {
    const jpg: string;
    export default jpg;
}

declare module "*.svg" {
    import React from "react";

    export const ReactComponent: React.FC<
        React.SVGProps<SVGSVGElement> & {
            alt?: string;
        }
    >;

    const src: string;
    export default src;
}
