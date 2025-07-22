import { useEffect, useRef } from "react";

// Increase the number of particles for a fuller background
const PARTICLE_COUNT = 150;

const ParticlesBackground = () => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const particles = useRef([]);
  const mouse = useRef({ x: undefined, y: undefined });

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    let width = window.innerWidth;
    let height = window.innerHeight;

    function createParticles() {
      particles.current = Array.from({ length: PARTICLE_COUNT }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        radius: Math.random() * 1.5 + 0.5,
        opacity: Math.random() * 0.5 + 0.3,
        pulse: Math.random() * Math.PI * 2,
      }));
    }

    function resize() {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
      createParticles();
    }

    function animate() {
      ctx.clearRect(0, 0, width, height);

      // Determine colors from CSS custom properties for theme-awareness
      const isDark = document.documentElement.classList.contains('dark');
      const particleColor = isDark ? '#a855f7' : '#10b981';
      const secondaryColor = isDark ? '#ec4899' : '#06b6d4';

      for (const p of particles.current) {
        // Mouse reactivity
        if (mouse.current.x !== undefined && mouse.current.y !== undefined) {
          const dx = p.x - mouse.current.x;
          const dy = p.y - mouse.current.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 120) { // Repel when close
            p.vx += dx / dist * 0.3;
            p.vy += dy / dist * 0.3;
          }
        }
        
        // Damping to slow down particles
        p.vx *= 0.98;
        p.vy *= 0.98;

        p.x += p.vx;
        p.y += p.vy;

        // Wrap around screen edges
        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        // Pulsing effect
        p.pulse += 0.02;
        const pulseRadius = p.radius + Math.sin(p.pulse) * 0.5;

        // Draw particle with alternating colors
        ctx.beginPath();
        ctx.arc(p.x, p.y, pulseRadius, 0, Math.PI * 2);
        
        // Alternate between primary and secondary colors
        const color = p.x % 100 < 50 ? particleColor : secondaryColor;
        ctx.fillStyle = color;
        ctx.globalAlpha = p.opacity;
        
        // Apply glow
        ctx.shadowColor = color;
        ctx.shadowBlur = 15;
        
        ctx.fill();
        ctx.globalAlpha = 1;
      }

      animationRef.current = requestAnimationFrame(animate);
    }

    function onMouseMove(e) {
      mouse.current.x = e.clientX;
      mouse.current.y = e.clientY;
    }

    // Initial setup and start animation
    resize();
    animationRef.current = requestAnimationFrame(animate);
    window.addEventListener("resize", resize);
    window.addEventListener("mousemove", onMouseMove);

    return () => {
      window.removeEventListener("resize", resize);
      window.removeEventListener("mousemove", onMouseMove);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []); // Reruns only on mount/unmount

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 w-full h-full -z-10 pointer-events-none"
      aria-hidden="true"
    />
  );
};

export default ParticlesBackground; 