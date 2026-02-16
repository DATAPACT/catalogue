<div class="tool-header">
  <h1>TOOLBOX UI</h1>
  <a href="https://assist-software.net/">
    <img src="./images/new-logo-lightblue.svg" alt="ASSISTLOGO">
  </a>
</div>

## **General Description**
**TOOLBOX UI** serves as the primary integration point for human-in-the-loop compliance tasks. It aggregates the interfaces of the underlying tools into a unified user interface.
Rather than accessing disparate services, users access the AI Legal Assistant for regulatory queries or the LexAlign visual editor directly through this portal via secure iframes. 
The portal handles the orchestration between these tools, allowing users to seamlessly transition from assessing a risk in the DPIA Support tool to viewing the final certification in the Compliance Result Manager. This unified frontend abstracts the underlying complexity of the microservices, providing a coherent, secure workflow for certification and reporting. 

## **Architecture**
[![TOOLBOX UI Architecture](./images/toolbox-ui-diagram.png)]

## **Commercial Information**
| Organisation (s) | License Nature | License |
| ASSIST Software | Proprietary, ASSIST ​ | Proprietary, ASSIST  |


# TOOLBOX UI
**ASSIST Software**

![TOOLBOX UI](./images/datapact-toolbox.png)


## **Related Project Links**
| Project Links |
| ------------- | 	
| GitHub Repository --> TOOLBOX UI <https://github.com/DATAPACT/toolbox-ui> |


## **How To Install**


First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
