on(construct){
   while(true)
   {
      if(false)
      {
         if(!ord("\t"))
         {
            break;
         }
      }
      else
      {
         §§push("\b");
      }
      if(ord(§§pop()))
      {
         while(true)
         {
            if(!getTimer())
            {
               §§push(getProperty(§§pop(), _X));
               break;
            }
            backgroundDown = "ButtonTransparentUp";
            backgroundUp = "ButtonTransparentUp";
            enabled = true;
            icon = "UI_QuestsBubble";
            §§push("label");
            §§push("");
            if(!ord("\t"))
            {
               continue;
            }
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
         }
         §§goto(addr14e3);
      }
      set(§§pop(),§§pop());
      break;
   }
   E = false;
   qZ = "\x1d{invalid_utf8=150}\x04";
   set("\b\b\x05",false);
   addr14e3:
}
