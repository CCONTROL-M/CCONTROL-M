interface PageTemplateProps {
  title: string;
}

const PageTemplate = ({ title }: PageTemplateProps) => {
  return (
    <div>
      <h1 className="page-title">{title}</h1>
      <p className="placeholder-text">Página em construção...</p>
    </div>
  );
};

export default PageTemplate; 